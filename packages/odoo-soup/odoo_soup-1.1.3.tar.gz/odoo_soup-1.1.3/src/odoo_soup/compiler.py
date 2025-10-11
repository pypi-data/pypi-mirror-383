from .config import get_config


def parse_fields(fieldsList: list) -> dict:
    fieldDict = {}
    for field in fieldsList:
        # Fields have optional string slicing indexes
        sliceStart = None
        sliceEnd = None

        # Format in config is arr with start and end pos, end pos optional
        if len(field) == 3:
            sliceStart = field[2][0]
            if len(field[2]) == 2:
                sliceEnd = field[2][1]

        fieldDict[field[0]] = {
            "index": field[1],
            "sliceStart": sliceStart,
            "sliceEnd": sliceEnd,
        }

    return fieldDict


def parse_config(version: str):
    # It is easier for user to configure logline types by alias rather than the search pattern, so some changes must be made here to read efficiently
    # Ensure that there are expected members of config for parsing log lines
    try:
        defaultIndexes = get_config()["default"]["default"]
    except KeyError:
        raise KeyError("Config is missing default parameters")

    """
    1. build a dict of search patterns mapped to alias, with the base default fields for all types of log lines
    2. update that dict with the default type specific field info
    2. if a non default version was configured, update the dict with the version specific info as well. return default config otherwise
    """

    # Populate the type mapping with the default options and overwrite any version specific things
    typeDefs = {}

    defaultTypes = get_config()["default"]
    defaultFields = parse_fields(defaultIndexes["fields"])
    # print(defaultTypes.items())

    for type, definition in defaultTypes.items():
        if type == "default":
            continue

        # Swap the alias and pattern for O(1) search while allowing easier config writing
        # Also add the default base mappings in
        temp = {"alias": type, "fields": defaultFields.copy()}

        # Check if there are type specific default mappings
        fields = definition.get("fields")

        if fields:
            fields = parse_fields(fields)
            temp["fields"].update(fields)

        typeDefs[definition["pattern"]] = temp

    # Now we overwrite the default options with version specific options if chosen by user

    if version != "default":
        versionSpecificTypes = get_config()[version]

        for type, definition in versionSpecificTypes.items():
            if type == "default":
                continue
            # Look up the pattern among existing mappings
            pattern = definition.get("pattern")

            # If the pattern is not a key in typedefs, that means we are redefining this mapping. So we need to look up the alias and swap to this search pattern
            if pattern not in typeDefs:
                # Find the key with matching alias
                for k, v in typeDefs.items():
                    if v["alias"] == type:
                        # If we found a record with matching alias, copy its contents to a new record with the new pattern, and delete old one
                        if pattern:
                            typeDefs[pattern] = v.copy()
                            del typeDefs[k]
                        else:
                            # Cover case where pattern was None so that a None key is not made
                            pattern = k
                        break

                # Add it in if it is truly not present at all
                if pattern is not None:
                    typeDefs[pattern] = {"alias": type, "fields": defaultFields.copy()}

            # Now that it is guaranteed to be in, we will update the record with the version specific info
            fields = definition.get("fields")
            if fields:
                definition["fields"] = parse_fields(fields)
                typeDefs[pattern]["fields"].update(definition["fields"])

    typeDefs["default"] = defaultFields

    return typeDefs
