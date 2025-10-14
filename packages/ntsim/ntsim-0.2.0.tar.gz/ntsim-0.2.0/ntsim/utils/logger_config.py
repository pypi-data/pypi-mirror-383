logger_config = {
    'version': 1, #requied
    'disable_existing_loggers': True,
    
    'formatters': {
        'std_format': {
#            'format': '[%(name)20s ] %(levelname)8s: %(message)s',
            'format': '[{name:>30s} ] {levelname}: {message}',
            'style': '{'
            }
        },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'std_format',
            }
        },
    'loggers': {
        'NTSim': {
            'level': 'WARNING',
            'handlers': ['console'],
            'propagate': False
            }
        },
    
#    'filters': {}
#    'root': {}
#    'incremental': True
}