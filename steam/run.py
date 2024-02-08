import arb
import csv

item_dict = {
    'trolling_graffities': {
        'url': 'https://steamcommunity.com/market/search?q=&category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Weapon%5B%5D=any&category_730_SprayCapsule%5B%5D=tag_csgo_spray_std2_drops_2&appid=730',
        'filename': 'trolling_graffities.csv',
    },
    'collection2_graffities': {
        'url': 'https://steamcommunity.com/market/search?q=&category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Weapon%5B%5D=any&category_730_SprayCapsule%5B%5D=tag_csgo_spray_std2_drops_1&appid=730',
        'filename': 'collection2_graffities.csv',
    },
    'collection3_graffities': {
        'url': 'https://steamcommunity.com/market/search?q=&category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Weapon%5B%5D=any&category_730_SprayCapsule%5B%5D=tag_csgo_spray_std3_drops&appid=730',
        'filename': 'collection3_graffities.csv',
    },
    'berlin_stickers': {
        'url': 'https://steamcommunity.com/market/search?q=&category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Weapon%5B%5D=any&category_730_StickerCategory%5B%5D=tag_PlayerSignature&category_730_StickerCategory%5B%5D=tag_TeamLogo&category_730_StickerCategory%5B%5D=tag_Tournament&category_730_Tournament%5B%5D=tag_Tournament16&appid=730',
        'filename': 'berlin_stickers.csv',
    },
    'rmr_stickers': {
        'url': 'https://steamcommunity.com/market/search?q=&category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Weapon%5B%5D=any&category_730_StickerCategory%5B%5D=tag_PlayerSignature&category_730_StickerCategory%5B%5D=tag_TeamLogo&category_730_StickerCategory%5B%5D=tag_Tournament&category_730_Tournament%5B%5D=tag_Tournament17&appid=730',
        'filename': 'rmr_stickers.csv',
    },
    'stockholm_stickers': {
        'url': 'https://steamcommunity.com/market/search?q=&category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Weapon%5B%5D=any&category_730_StickerCategory%5B%5D=tag_PlayerSignature&category_730_StickerCategory%5B%5D=tag_TeamLogo&category_730_StickerCategory%5B%5D=tag_Tournament&category_730_Tournament%5B%5D=tag_Tournament18&appid=730',
        'filename': 'stockholm_stickers.csv',
    },
    'rio_stickers': {
        'url': 'https://steamcommunity.com/market/search?q=&category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Weapon%5B%5D=any&category_730_StickerCategory%5B%5D=tag_PlayerSignature&category_730_StickerCategory%5B%5D=tag_TeamLogo&category_730_StickerCategory%5B%5D=tag_Tournament&category_730_Tournament%5B%5D=tag_Tournament20&appid=730',
        'filename': 'rio_stickers.csv',
    },
    'antwerp_stickers': {
        'url': 'https://steamcommunity.com/market/search?q=&category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Weapon%5B%5D=any&category_730_StickerCategory%5B%5D=tag_PlayerSignature&category_730_StickerCategory%5B%5D=tag_TeamLogo&category_730_StickerCategory%5B%5D=tag_Tournament&category_730_Tournament%5B%5D=tag_Tournament19&appid=730',
        'filename': 'antwerp_stickers.csv',
    },
    'paris_stickers': {
        'url': 'https://steamcommunity.com/market/search?q=&category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Weapon%5B%5D=any&category_730_StickerCategory%5B%5D=tag_PlayerSignature&category_730_StickerCategory%5B%5D=tag_TeamLogo&category_730_StickerCategory%5B%5D=tag_Tournament&category_730_Tournament%5B%5D=tag_Tournament21&appid=730',
        'filename': 'paris_stickers.csv',
    },
    'cases':  {
        'url': 'https://steamcommunity.com/market/search?q=Case&category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Weapon%5B%5D=any&category_730_Type%5B%5D=tag_CSGO_Type_WeaponCase&appid=730',
        'filename': 'cases.csv',
    }
}

def scrape(collection, account: arb.SteamBot):
    item_data = account.scrape_market(item_dict[collection]['url'])

    ################ scrape_market parsing ################
    csv_file = item_dict[collection]['filename']

    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)

        # Write the data rows
        for row in item_data:
            print(row)
            writer.writerow(row)

def scrape_task(account, mode='all'):
    if mode == 'all':
        for collection in item_dict:
            scrape(collection, account)
    else:
        scrape(mode, account)


if __name__ == '__main__':
    cad = ['Username1:Password1']
    php = ['Username2:Psssword2']
    bot = arb.SteamBot(cad)

    bot.login()

    scrape_task(bot, mode='cases')
