import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)


def apply_hardcoded_cases(llm_response: dict) -> None:
    logger.info("Looking for hardcoded exceptions for LLM response.")

    if "hermes" in llm_response.get("client", {}).get("name", "").lower():
        logger.info("Client is 'Hermes', exceptions might apply...")
        swap_sender_receiver_for_hermes(llm_response)
        return

    if "xxxlutz" in llm_response.get("client", {}).get("name", "").lower():
        logger.info("Client name is 'XXXLutz', exceptions migh apply...")
        add_return_transport_for_xxxlutz(llm_response)
        return

    if "mondi" in llm_response.get("client", {}).get("name", "").lower():
        logger.info("Client name is 'Mondi', exceptions might apply...")
        add_delivery_date_for_mondi(llm_response)
        return
    if "nagel" in llm_response.get("client", {}).get("name", "").lower():
        logger.info("Client name is 'Nagel', exceptions might apply...")
        check_date_for_nagel(llm_response)
        return

    logger.info("No hardcoded exceptions found.")
    return


def add_delivery_date_for_mondi(llm_response: dict) -> None:
    """Adds a delivery date for Mondi if it is not present."""
    logger.info("Attempting to add delivery date for Mondi.")
    transports: list[dict] = llm_response.get("transports", [])
    for transport in transports:
        loading_date = datetime.strptime(
            transport.get("loadingDate", [""])[0], "%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=ZoneInfo("Europe/Berlin"))
        # set delivery date next day at 6 am
        delivery_date = loading_date + timedelta(days=1)
        delivery_date = delivery_date.replace(hour=6, minute=0, second=0)
        transport["deliveryDate"] = [delivery_date.strftime("%Y-%m-%d %H:%M:%S")]
        logger.info(
            "Added delivery date for Mondi transport: %s",
            transport["deliveryDate"][0],
        )


def set_momax_as_client_for_xxxlutz(llm_response: dict) -> None:
    """Sets Mömax as client if it is found as sender in any transport."""
    for transprot in llm_response.get("transports", []):
        sender = transprot.get("sender", {})
        sender_name = sender.get("name", "").lower()
        if "mömax" in sender_name.lower():
            logger.info("Found Mömax as sender, setting to client.")
            client_dict = llm_response.get("client", {})
            client_dict["city"] = sender.get("city", "")
            client_dict["country"] = sender.get("country", "")
            client_dict["houseNumber"] = sender.get("houseNumber", "")
            client_dict["name"] = sender.get("name", "")
            client_dict["street"] = sender.get("street", "")
            client_dict["zip"] = sender.get("zip", "")
            llm_response["client"] = client_dict
            logger.info("Set Mömax as client.")
            logger.info("New client data: %s", llm_response["client"])
            return


def swap_sender_receiver_for_hermes(llm_response: dict) -> None:
    tranports = llm_response.get("transports", [])
    for transport in tranports:
        sender = transport.get("sender", {})
        receiver = transport.get("receiver", {})

        sender_city = sender.get("city", "").lower()
        receiver_city = receiver.get("city", "").lower()

        if (
            "mülheim" in sender_city or "kaiserslautern" in sender_city
        ) and "ansbach" in receiver_city:
            # swap them
            transport["sender"], transport["receiver"] = (
                transport["receiver"],
                transport["sender"],
            )
            logger.info(
                "Swapped sender and receiver for Hermes transport (now: %s -> %s)",
                sender_city,
                receiver_city,
            )


def add_return_transport_for_xxxlutz(llm_response: dict) -> None:
    """Adds a return transport for XXXLutz if it is not present."""
    logger.info("Attempting to add return transports for XXXLutz.")
    try:
        transports: list[dict] = llm_response.get("transports", [])
        return_transports = []
        for transport in transports:
            loading_date = transport.get("loadingDate", [""])[0]
            loading_date = datetime.strptime(loading_date, "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=ZoneInfo("Europe/Berlin")
            )

            delivery_date = transport.get("deliveryDate", [""])[0]
            delivery_date = datetime.strptime(
                delivery_date, "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=ZoneInfo("Europe/Berlin"))

            sender = transport.get("sender", {})
            receiver = transport.get("receiver", {})
            carrier = transport.get("carrier", {})
            return_transport = {
                "order_nr": None,
                "pallets": None,
                "pieces": None,
                "cartons": None,
                "customer_ref": None,
                "deliveryDate": [delivery_date.strftime("%Y-%m-%d %H:%M:%S")],
                "deliverRefNr": None,
                "loadingDate": [delivery_date.strftime("%Y-%m-%d %H:%M:%S")],
                "loadingRefNR": None,
                "sender": receiver,
                "receiver": sender,
                "carrier": carrier,
                "volume": None,
                "weight": 0.0,
                "goods": {
                    "number_of_rolls": None,
                    "gross_weight_kg": None,
                    "net_weight_kg": None,
                    "pallets": None,
                    "loading_space_meters": None,
                },
            }
            return_transports.append(return_transport)
        if return_transports:
            # insert return transport after each original transport
            print("Adding return transports for XXXLutz.")
            new_transports = []
            for original_transport, return_transport in zip(
                transports, return_transports, strict=True
            ):
                new_transports.append(original_transport)
                new_transports.append(return_transport)
            llm_response["transports"] = new_transports
            logger.info("Added return transport for XXXLutz.")

        transports = llm_response.get("transports", [])
        for i, transport in enumerate(transports):  # fix loading dates
            if i > 0:
                transport["loadingDate"] = transports[i - 1].get("deliveryDate", [""])

    except Exception:
        print("Failed to add return transport for XXXLutz.")
        logger.exception("Failed to add return transport for XXXLutz.")


def check_date_for_nagel(llm_response: dict) -> None:
    """Checks and corrects the loading and delivery dates for Nagel if they seem to have day and month swapped."""
    try:
        logger.info("Attempting to check and correct dates for Nagel.")
        transports = llm_response.get("transports", [])
        for transport in transports:
            today = datetime.now(ZoneInfo("Europe/Berlin"))
            loading_date_str = transport.get("loadingDate", [""])[0]
            loading_date = datetime.strptime(
                loading_date_str, "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=ZoneInfo("Europe/Berlin"))
            if (
                loading_date.date().month != today.date().month
                and loading_date.date().month
                != (today + timedelta(weeks=1)).date().month
            ):
                logger.info(
                    "Loading date month (%s) does not match current month (%s). Possibly they are swapped.",
                    loading_date.date().month,
                    today.date().month,
                )
                # switch date and month
                new_loading_date = loading_date.replace(
                    month=loading_date.day, day=loading_date.month
                )
                transport["loadingDate"] = [
                    new_loading_date.strftime("%Y-%m-%d %H:%M:%S")
                ]
                logger.info(
                    "Corrected loading date for Nagel transport: %s",
                    transport["loadingDate"][0],
                )
            delivery_date = transport.get("deliveryDate", [""])[0]
            if delivery_date:
                delivery_date = datetime.strptime(
                    delivery_date, "%Y-%m-%d %H:%M:%S"
                ).replace(tzinfo=ZoneInfo("Europe/Berlin"))
                if (
                    delivery_date.date().month != today.date().month
                    and delivery_date.date().month
                    != (today + timedelta(weeks=1)).date().month
                ):
                    logger.info(
                        "Delivery date month (%s) does not match current month (%s). Possibly they are swapped.",
                        delivery_date.date().month,
                        today.date().month,
                    )
                    # switch date and month
                    new_delivery_date = delivery_date.replace(
                        month=delivery_date.day, day=delivery_date.month
                    )
                    transport["deliveryDate"] = [
                        new_delivery_date.strftime("%Y-%m-%d %H:%M:%S")
                    ]
                    logger.info(
                        "Corrected delivery date for Nagel transport: %s",
                        transport["deliveryDate"][0],
                    )
    except Exception:
        logger.exception("Failed to check and correct dates for Nagel.")
