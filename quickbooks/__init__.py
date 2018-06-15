import os
DEV_ENV=os.environ.get("ENV")
print(DEV_ENV)
if DEV_ENV=="HEROKU":
    YA_DEVELOPER_TOKEN=os.environ.get("YELLOWANT_DEVELOPER_TOKEN")

    base=os.environ.get("HEROKU_APP_NAME")
    website = "https://{}.herokuapp.com/".format(base)
    os.system("yellowant auth --token {} --host https://www.yellowant.com ".format(YA_DEVELOPER_TOKEN))
    os.system('yellowant sync -q --api_url {}yellowant-api/ --website {} --install_page_url {} --privacy_policy_url {}privacy --redirect_uris {}yellowantredirecturl/'.format(website,website,website,website,website))
    os.system('ls -al')

