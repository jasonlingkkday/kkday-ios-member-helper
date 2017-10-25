import localization_helper

def example_read_google_spreadsheet():
    # create spreadsheet_manager
    spreadsheet_manager = localization_helper.SpreadSheetManager()
    # load config file
    config = localization_helper.Config(file_path='workspace/config.json')
    # read parameters from config
    scopes = config.get("spreadsheet.google.scope")
    secret_file = "workspace/" + config.get("spreadsheet.google.secret")
    spreadsheet_id = config.get("spreadsheet.spreadsheetId")
    range_name = spreadsheet_manager.create_range(sheet_name=config.get("spreadsheet.sheetName"), 
                                                  start_row=config.get("spreadsheet.startRow"), 
                                                  end_row=config.get("spreadsheet.endRow"), 
                                                  start_col=config.get("spreadsheet.startCol"), 
                                                  end_col=config.get("spreadsheet.endCol"))
    # read google spreadsheet
    rows = spreadsheet_manager.download_spreadsheet(scopes=scopes, 
                                                    secret_file=secret_file, 
                                                    spreadsheet_id=spreadsheet_id, 
                                                    range_name=range_name)
    # parse rows from above
    entries = spreadsheet_manager.parse_spreadsheet(spreadsheet_rows=rows, 
                                                    key_lang=config.get("spreadsheet.keyLanguage"), 
                                                    lang_col_mapping=config.get("spreadsheet.languageCols"))
    # write the result disk
    filename = 'spreadsheet.json'
    spreadsheet_manager.save_entries_to_disk(entries=entries, filename=filename)
    print('done!')

if __name__ == '__main__':
    example_read_google_spreadsheet()