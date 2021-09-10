from loguru import logger as l

l.add(
    "general.log",
    mode="w",
    rotation="10MB",
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
)
for _ in range(5):
    l.info("#" * 50)

logger = l
