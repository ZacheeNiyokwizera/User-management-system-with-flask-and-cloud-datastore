from decouple import config


def get_datastore_emulator_host():
    return config('DATASTORE_EMULATOR_HOST', default='default_value_for_datastore_host')


def get_google_cloud_project():
    return config('GOOGLE_CLOUD_PROJECT', default='default_value_for_google_cloud_project')
