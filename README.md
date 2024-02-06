# logistics

## Installasjon

### Dependencies

Må laste ned [Appscript](https://appscript.sourceforge.io/) til Python for å bruke `send-update.py`-skriptet (trengs for å sende eposter med Outlook epostclienten:

`pip3 install appscript`

### Mottakerliste

For å bruke skriptet `send-update.py` trengs en mottakerliste i CSV-filformat. Filen bør være på formen:

`lagerId;lager;epost`

### Oppdatere config-filene

Det er to config-filer som må oppdateres før scriptene fungerer: `config.ini` i `src/run/` og `front.config.ini` i `src/externapi/front`. Oppdater verdien til `UtilPath` under `[env]` i `config.ini` til absolutt filsti til `src`-mappa (f.eks. `Users/olanordmann/pythonscripts/logistics/src`
), og verdien til `RecipientFile` under `[email]` til absolutt filsti til mottakerliste-filen beskrevet ovenfor (f.eks. `/Users/olanordmann/pythonscripts/mottakerliste.csv`).

