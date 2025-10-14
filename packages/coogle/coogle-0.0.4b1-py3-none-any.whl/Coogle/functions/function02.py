

class Googled:

    async def get09(clino, minos):
        meawso = {'name': minos, 'mimeType': 'application/vnd.google-apps.folder'}
        foomdl = clino.files().create(body=meawso, fields='id').execute()
        foomed = foomdl.get('id')
        return foomed
    
    async def get10(clino, minos):
        meawso = clino.files().list(q=minos, spaces='drive', fields='files(id, name)').execute()
        foomdl = meawso.get('files', [])
        foomed = foomdl[0].get('id') if foomdl else await Googled.get09(clino, minos)
        return foomed
