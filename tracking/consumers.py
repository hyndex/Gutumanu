from channels.generic.websocket import AsyncJsonWebsocketConsumer


class AlertConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.resume_token = self.scope.get('query_string', b'').decode().replace('token=', '') or None
        await self.accept()
        await self.send_json({'type': 'connected', 'resume_token': self.resume_token})

    async def receive_json(self, content, **kwargs):
        msg_type = content.get('type')
        if msg_type == 'heartbeat':
            await self.send_json({'type': 'heartbeat'})
        elif msg_type == 'resume':
            self.resume_token = content.get('token')
            await self.send_json({'type': 'resume', 'token': self.resume_token})

    async def send_alert(self, event):
        data = event['data']
        token = event.get('token')
        await self.send_json({'type': 'alert', 'data': data, 'token': token})
