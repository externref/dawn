import dawn

bot = dawn.Bot("TOKEN")

bot.load_module("extension_module")  # python import path like stucture.

bot.run()
