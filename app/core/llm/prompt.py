def get_prompt(input, retrieved):
    context = ""
    for item in retrieved:
        context = " ".join([context, item["text"]])

    system_prompt = "You are a retail sales analyst for Superstore (2014-2017). You answer the question provided by the user. "
    #context_prompt = "Answer the question using the following context:"
    rules = "If the context provided does not contain the requiered infomation, tell the user the data is insufficent."
    system_prompt = system_prompt + rules
    return system_prompt, context