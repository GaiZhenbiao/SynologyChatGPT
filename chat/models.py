from django.db import models
import json

# Create your models here.

class ChatGPTConfiguration(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    openAI_API_Key = models.CharField(max_length=200)
    bot_Key = models.CharField(max_length=200)
    history = models.TextField(default="[]")
    total_token = models.IntegerField(default=0)
    base_url = models.CharField(max_length=256, default="http://127.0.0.1:5001")

    def bot_url(self):
        return f"{self.base_url}/webapi/entry.cgi?api=SYNO.Chat.External&method=chatbot&version=2&token=%22{self.bot_Key}%22"

    def get_history(self):
        return json.loads(self.history)

    def save_history(self, context, tokencount):
        self.history = json.dumps(context)
        self.total_token = tokencount
        self.save()

    def clear_history(self):
        self.history = "[]"
        self.total_token = 0
        self.save()