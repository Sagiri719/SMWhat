python -m PyInstaller --onefile -w ^
--icon=res\icon.ico ^
--add-data "settings.json;." ^
--add-data "LICENSE;." ^
--add-data "persistence\data.json;persistence" ^
--add-data "presentation\languages;presentation\languages" ^
--add-data "res;res" ^
--add-data "plugins;plugins" ^
main.py
