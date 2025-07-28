from investiny import search_assets

res = search_assets(query='CSTR',limit=1,
                    type='Stock')
#fullname= 'Fomo Worldwide, Inc.'
print(res)

#"CSTR", "01/01/2023", "31/05/2023"
