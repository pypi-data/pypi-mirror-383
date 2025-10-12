from wisort.config import Config, loaded


def use_runes():
    for name, lib in loaded.libraries:
        for attr, value in vars(lib).items():
            if not isinstance(value, str):
                continue
            if value.startswith("@"):
                if value[1:] not in loaded.runes:
                    print(f"`rune {value[1:]}` not found in your config")
                    continue
                setattr(loaded.libraries[name], attr, loaded.runes[value[1:]])
                # TODO: add type checking
