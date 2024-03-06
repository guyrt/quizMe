

def populate_default_settings(user):
    from users.models import LooseUserSettings

    defaults = [
        {
            "key": LooseUserSettings.KnownKeys.DomainExclude,
            "value": "microsoft-my.sharepoint.com",
        },
        {
            "key": LooseUserSettings.KnownKeys.DomainExclude,
            "value": "outlook.office.com",
        },
        {
            "key": LooseUserSettings.KnownKeys.DomainExclude,
            "value": "microsoft.sharepoint.com",
        },
        {"key": LooseUserSettings.KnownKeys.DomainExclude, "value": "localhost"},
        {
            "key": LooseUserSettings.KnownKeys.DomainExclude,
            "value": "totalrewards.azurefd.net",
        },
        {
            "key": LooseUserSettings.KnownKeys.DomainExclude,
            "value": "statics.teams.cdn.office.net",
        },
        {
            "key": LooseUserSettings.KnownKeys.DomainExclude,
            "value": "microsoft-my.sharepoint-df.com",
        },
        {
            "key": LooseUserSettings.KnownKeys.DomainExclude,
            "value": "ms.portal.azure.com",
        },
        {"key": LooseUserSettings.KnownKeys.DomainExclude, "value": "sapsf.com"},
        {
            "key": LooseUserSettings.KnownKeys.DomainExclude,
            "value": "idweb.microsoft.com",
        },
        {
            "key": LooseUserSettings.KnownKeys.DomainExclude,
            "value": "login.microsoftonline.com",
        },
        # banks
        {
            "key": LooseUserSettings.KnownKeys.DomainExclude,
            "value": "https://digital.fidelity.com",
        },
    ]

    user_defaults = [LooseUserSettings(user=user, **setting) for setting in defaults]
    LooseUserSettings.objects.filter(user=user).delete()
    LooseUserSettings.objects.bulk_create(user_defaults)
