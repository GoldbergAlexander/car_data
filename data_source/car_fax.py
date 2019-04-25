import pandas


def get_car_fax(url='', vin=''):

    if len(vin) > 0:
        url = f'https://www.carfax.com/VehicleHistory/p/Report.cfx?vin={vin}'

    dfs = pandas.read_html(url)

    summary = dfs[1]

    accident = summary[1][0]    # No accidents reported to CARFAX
    damage = summary[1][1]      # No damage reported to CARFAX
    owners = summary[1][2]      # 3 Previous owners

    accident = (accident != 'No accidents reported to CARFAX')
    damage = (damage != 'No damage reported to CARFAX')
    if owners == 'CARFAX 1-Owner vehicle':
        owners = 1
    else:
        try:
            owners = int(owners.split(' ')[0])
        except Exception as e:
            print(f'Error processing Car Fax')
            print(summary)

    return accident, damage, owners



