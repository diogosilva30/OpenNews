from app.core.common.custom_exceptions import RequestError

supported_journals = ["publico"]


def check_if_journal_is_support(j: str) -> None:
    j = str(j)
    if j in supported_journals:
        return True
    else:
        raise RequestError("Jornal with name {} is not supported!".format(j))


def get_supported_journals():
    return supported_journals.sort()
