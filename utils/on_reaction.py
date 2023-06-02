from config import *
import nextcord
import re
import asyncio


async def payement(bot, payload):
    from utils.embedder import embed_success, embed_warning, embed_error

    guild = await bot.fetch_guild(payload.guild_id)
    chan = await guild.fetch_channel(payload.channel_id)
    message = await chan.fetch_message(payload.message_id)
    user = await guild.fetch_member(payload.user_id)

    admin = settings.admin
    modo = settings.modo
    rl_op = settings.rl_op
    rl = settings.rl
    rl_test = settings.rl_test
    rh = settings.rh

    roles_requis = [admin, modo, rl_op, rl, rl_test, rh]
    user_roles = [role.id for role in user.roles]

    # Vérifie que la personne peut faire le payement
    a_role_requis = any(role_id in user_roles for role_id in roles_requis)
    if not a_role_requis:
        return

    sanctionne = None

    # Vérifier si le message contient une mention
    if message.embeds:
        for embed in message.embeds:
            if isinstance(embed.description, str):
                match = re.search(r"<@(\d+)>", embed.description)
            if match:
                user_id = int(match.group(1))
                sanctionne = await guild.fetch_member(user_id)
            else:
                error_msg = await chan.send(
                    embed=embed_error(
                        "", "Le message auquel vous avez réagi n'est pas une sanction !"
                    )
                )
                logger.warning(
                    f"- Le message sur lequel {user.display_name} a réagi n'est pas une sanction !.\n"
                )
                await asyncio.sleep(10)
                await error_msg.delete()
                logger.info(f"Échec:\n")
                return

    logger.info(
        f"+ {user.display_name} souhaite confirmer le payement de {sanctionne.display_name}"
    )

    confirmation_message = await chan.send(
        embed=embed_warning(
            "", f"{user.mention}, confirmez-vous le paiement de {sanctionne.mention} ?"
        )
    )
    await confirmation_message.add_reaction("👍")  # Réaction pour la confirmation
    await confirmation_message.add_reaction("👎")  # Réaction pour le refus

    try:
        reaction, _ = await bot.wait_for(
            "reaction_add",
            check=lambda r, u: r.message == confirmation_message and u == user,
            timeout=15,
        )
        if reaction.emoji == "👍":
            logger.info(f"+ {user.display_name} a confirmé !")

            if payload.channel_id == settings.chan_deserteur:
                try:
                    from cogs.sanctions.Deserteur import pardon

                    await pardon(user, sanctionne)
                    logger.info(
                        f"+ {sanctionne.display_name} a réglé ses dettes, il n'est plus déserteur !"
                    )
                    await chan.send(
                        embed=embed_success(
                            "",
                            f"{sanctionne.mention} a réglé ses dettes, il n'est plus déserteur !\n",
                        )
                    )
                    await message.delete()
                    logger.info("Succès !\n")
                except Exception as e:
                    logger.error(f"Échec : {e}")

            elif payload.channel_id == settings.chan_sanction:
                await chan.send(
                    embed=embed_success("", f"{sanctionne.mention} a réglé ses dettes !")
                )
                logger.info(f"+ {sanctionne.display_name} a réglé ses dettes !")
                role = nextcord.utils.get(guild.roles, id=settings.sanctionne)
                await sanctionne.remove_roles(role)
                logger.info(f"+ rôle sanction enlevé.")
                await message.delete()
                logger.info("Succès !\n")

        elif reaction.emoji == "👎":
            logger.info(f"- {user.display_name} a abandonné !\n")
            # Supprimer la réaction de la personne sur le message initial
            await message.remove_reaction(payload.emoji, user)
            logger.info(f"Échec:\n")

    except asyncio.TimeoutError:
        logger.info(f"- {user.display_name} n'a pas réagit !\n")
        # Supprimer la réaction de la personne sur le message initial
        await message.remove_reaction(payload.emoji, user)
        logger.info(f"Échec:\n")

    # Supprimer le message de confirmation
    await confirmation_message.delete()
