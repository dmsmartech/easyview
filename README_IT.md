[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/dmsmartech/easyview)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

[🇬🇧 English](README.md) | 🇮🇹 Italiano

---

# Medtrum EasyView — Integrazione per Home Assistant

Questa integrazione permette di visualizzare in Home Assistant i dati glicemici in tempo reale dei sensori CGM **Medtrum**, letti tramite il cloud **EasyView**.

---

## Come funziona

Il sensore CGM Medtrum trasmette i dati all'app **EasyView** sul telefono del paziente. Tramite la funzione di condivisione Follow, questi dati vengono inviati in cloud e resi disponibili a un secondo account tramite la funzione **EasyView Follow**.

L'integrazione per Home Assistant si collega a questo account Follow per leggere i dati in tempo reale.

---

## Prerequisiti

- Un sensore CGM Medtrum attivo
- L'app **EasyView** installata sul telefono del paziente, con un account Medtrum registrato
- Un **secondo account Medtrum** da usare come account Follow (può essere un tuo account secondario)
- Home Assistant con HACS installato

---

## Passo 1 — Invitare l'account Follow da EasyView

Sul telefono del paziente, nell'app **EasyView**:

1. Apri l'app e vai su **Impostazioni**
2. Seleziona **Follow** o **Condivisione**
3. Inserisci l'indirizzo email del secondo account
4. Invia l'invito

---

## Passo 2 — Accettare l'invito e verificare l'accesso

Sul dispositivo dove hai ricevuto l'invito:

1. Accetta l'invito tramite l'email o la notifica ricevuta
2. Accedi all'account EasyView Follow
3. Verifica che i dati glicemici del paziente siano visibili

---

## Passo 3 — Installare l'integrazione in Home Assistant

### Tramite HACS

1. Apri HACS in Home Assistant
2. Vai su **Integrazioni** → clicca sui tre puntini in alto a destra → **Repository personalizzati**
3. Inserisci l'URL del repository: `https://github.com/dmsmartech/easyview`
4. Seleziona la categoria **Integrazione**
5. Clicca **Aggiungi**
6. Cerca **EasyView** in HACS e installala
7. Riavvia Home Assistant

### Installazione manuale

1. Copia la cartella `custom_components/easyview` nella directory `custom_components` di Home Assistant
2. Riavvia Home Assistant

---

## Passo 4 — Configurare l'integrazione

1. In Home Assistant vai su **Impostazioni** → **Dispositivi e servizi**
2. Clicca **Aggiungi integrazione** e cerca **EasyView**
3. Inserisci:
   - **Email** e **Password** dell'account EasyView Follow
   - **Unità di misura** — `mg/dL` oppure `mmol/L`
   - **Soglia glicemia alta** — valore oltre il quale si attiva il sensore *È Alto* (default: 180 mg/dL)
   - **Soglia glicemia bassa** — valore sotto il quale si attiva il sensore *È Basso* (default: 70 mg/dL)
4. Clicca **Invia**

Se le credenziali sono corrette, l'integrazione si connette e i sensori vengono creati automaticamente.

---

## Sensori disponibili

Per ogni utente monitorato vengono creati:

| Sensore | Descrizione |
|---|---|
| Glicemia | Valore attuale in mg/dL o mmol/L |
| Tendenza glicemia | Testo + icona (Stabile, In aumento, In diminuzione, ecc.) |
| Stato sensore | Normale / Riscaldamento / Necessita calibrazione |
| Batteria | Percentuale batteria del sensore |
| Minuti dall'ultimo aggiornamento | Minuti passati dall'ultima lettura |
| È Alto | Attivo / Non attivo (soglia configurabile) |
| È Basso | Attivo / Non attivo (soglia configurabile) |

---

## Modifica delle soglie di allerta

Le soglie possono essere modificate in qualsiasi momento senza reinstallare l'integrazione:

1. In Home Assistant vai su **Impostazioni** → **Dispositivi e servizi**
2. Trova l'integrazione **EasyView** e clicca sull'icona ✏️ **Configura**
3. Aggiorna la **Soglia glicemia alta** e/o la **Soglia glicemia bassa**
4. Clicca **Invia**

---

## Re-autenticazione

Se l'integrazione smette di funzionare a causa di una sessione scaduta:

1. In Home Assistant vai su **Impostazioni** → **Dispositivi e servizi**
2. Troverai una notifica sull'integrazione EasyView — clicca **Re-autenticare**
3. Reinserisci le credenziali

Non è necessario rimuovere e reinstallare l'integrazione.

---

## Problemi comuni

| Problema | Soluzione |
|---|---|
| Errore di autenticazione | Verifica email e password dell'account Follow |
| Nessun dato visibile | Verifica che l'invito sia stato accettato e i dati siano visibili nell'account Follow |
| Sensori non disponibili | Controlla la connessione internet e riavvia l'integrazione |
| Batteria mostra valore errato | Aggiorna all'ultima versione dell'integrazione |

---

## Crediti

Sviluppato da [dmsmartech](https://github.com/dmsmartech).  
Utilizzo API basato sul progetto open source [nl-ruud/nightscout-easyview](https://github.com/nl-ruud/nightscout-easyview).
