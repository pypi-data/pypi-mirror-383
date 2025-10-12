EMOJI = "⭐🎄⏰☁⏳☀☂☃☎☕☘☣🙁🙂♻⚡⚽⚾⛏✂✅✈✉✏❌❓❗❤🆒🌈🌉🌊🌋🌍🌕🌡🌧🌪🌭🌮🌲🌵🌶🌻🌽🍁🍄🍇🍉🍌🍎🍑🍓🍔🍕🍗🍙🍛🍝🍞🍟🍣🍆🍤🍦🍩🍪🍫🍬🍭🍯🍰🍴🍷🍺🍼🍿🎁🎃🎅🎆🎈🎉🎐🎗🎟🎡🎤🎥🎧🎨🎩🎪🎮🎱🎲🎳🎵🎷🎸🎹🏀🏅🏆🏈🏓🏔🐆🏧🏭🏮🏳🏹🐀🐄🐅🏠🐇🐈🐉🐊🐋🐌🐍🐎🐐🐑🏰🐒🐓🐕🐖🐘🐙🐛🐝🐞🐟🐢🐧🐪🐬👀👁👂👃👄👅👓👖👗👢👮👰👺👻👽💃💄💉💊💎💡💢💣💤💥💧💪💯💰💳💾💿📁📃📆📈📋📌📎📏📕📦📷📺📼🔊🔋🔌🔍🔑🔒🔔🔥🔦🔧🔨🔫🕵🕷🕸🕹🖕🖖🗿🗺😂😏😡😤😬😭😱🚀🚁🚂🚒🚓🚲🚿🛌🛑🛒🛴🛸🤖🤠🤔🥐🥑🥒🥓🥔🥕🥖🥗🥚🥛🥜🥝🥞🥧🥨🥩🥪🦀🦇🦊🦋🦖🧙🧛🧜🧦👾"  # noqa: E501


def ip_to_emoji(ip: str):
    try:
        parts = ip.split(".")
        if len(parts) != 4:
            return ip
        r = ""
        for p in parts:
            r += EMOJI[int(p)]
        return r
    except Exception:
        return ip


def emoji_to_ip(emoji: str):
    try:
        if len(emoji) != 4:
            return ""
        r: list[int] = []
        for e in emoji:
            r.append(EMOJI.index(e))
        return ".".join(map(str, r))
    except Exception:
        return ""
