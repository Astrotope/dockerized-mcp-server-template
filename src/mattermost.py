from mattermostdriver import Driver

foo = Driver({
    'url': 'mattermost-astrotope.sliplane.app',
    'login_id': 'astrotope',
    'password': 'T3k5Fqs7FaVU9LO',
    'token': 'bbsjobqfwfdzifkcgyudc67imy',
    'scheme': 'https',
    'port': 443,
    'basepath': '/api/v4'
})

foo.login()

channel_id = foo.channels.get_channel_by_name_and_team_name('astrotopeorg', 'mcp')['id']

print(channel_id)

foo.posts.create_post(options={
    'channel_id': channel_id,
    'message': 'This is the important file'})
