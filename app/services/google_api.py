from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings


FORMAT = '%Y/%m/%d %H:%M:%S'


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheet_body = {
        'properties': {'title': f'Отчет на {now_date_time}',
                       'locale': 'ru_RU'},
        'sheets': [{'properties': {'sheetType': 'GRID',
                                   'sheetId': 0,
                                   'title': 'Лист 1',
                                   'gridProperties': {'rowCount': 100,
                                                      'columnCount': 11}}}]
    }
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    return response['spreadsheetId']


async def set_user_permission(
        spreadsheetId: int,
        wrapper_services: Aiogoogle
) -> None:
    print(spreadsheetId)
    permissions_body = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': settings.email_user
    }
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheetId,
            json=permissions_body,
            fields='id'
        )
    )


async def spreadsheets_update_value(
    spreadsheetId: str,
    reservations: list,
    wrapper_services: Aiogoogle
) -> None:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    table_values = [
        ['Отчет от', now_date_time],
        ['Количество регистраций переговорок'],
        ['ID переговорки', 'Кол-во бронирований']
    ]
    for res in reservations:
        table_values.append([str(res['meetingroom_id']), str(res['count'])])
    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheetId,
            range='A1:E30',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
