def get_prompt(retrieved):
    context = ""
    for item in retrieved:
        context = " ".join([context, item["text"]])
    return context