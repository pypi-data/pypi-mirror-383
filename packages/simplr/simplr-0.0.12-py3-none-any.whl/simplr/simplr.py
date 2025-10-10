from sys import argv

def run_cli():
    from .Agent import create_and_run_cli
    create_and_run_cli()

def main():

    if len(argv) > 1:
        if argv[1] == "run":
            run_cli()
        elif argv[1] == "clear_cache":
            from .Cache import Cache
            Cache._clear_cache()
        elif argv[1] == "config":
            from .Config import Config, get_config
            Config._clear_cache()
            get_config()
        else:
            if len(argv) > 1:
                from .Agent import create_and_run_agent
                create_and_run_agent(" ".join(argv[1:]))
    else:
        run_cli()

