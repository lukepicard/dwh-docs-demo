---
title: Glossario
nav_order: 3
---

# Glossario

Termini usati nella documentazione del data warehouse dimostrativo.

| Termine | Significato |
|---|---|
| **Causale** | Il motivo di un movimento (bonifico, stipendio, pagamento con carta, prelievo, …). Ha un segno: + il denaro entra, − esce. Configurata in [`DC_DIM_CAUSALE`](oggetti/DC_DIM_CAUSALE.md). |
| **Control-M** | Lo schedulatore che lancia le shell. Legge il return code: `0` ok, `1` errore, `2` semaforo KO (ritenta), `3` errore workflow. |
| **Controvalore** | Quanto vale un dossier a fine mese: quantità di ogni titolo per il suo prezzo. Per le obbligazioni il prezzo è una percentuale, quindi si divide per 100. Vedi [`DI_FT_CONTROVALORI_MENSILI`](oggetti/DI_FT_CONTROVALORI_MENSILI.md). |
| **Data contabile** | Il giorno in cui un movimento conta per il saldo (`DAT_CONTABILE`). È la data dei saldi mensili e della partizione dei movimenti. |
| **Data di riferimento** | Il giorno a cui si riferisce il file (`DAT_RIFERIMENTO`); per i saldi, l'ultimo giorno del mese. Parametro `-d YYYYMMDD` delle shell. |
| **Data valuta** | Il giorno da cui decorrono gli interessi di un movimento (`DAT_VALUTA`). Può essere diversa dalla data contabile. Non entra nei saldi. |
| **Doppione** | Lo stesso movimento presente due volte nel file della fonte. Si riconosce dall'identificativo (`ID_MOVIMENTO`) e ne resta uno solo in [`DC_FT_MOVIMENTI`](oggetti/DC_FT_MOVIMENTI.md). |
| **Dossier** | Il contenitore dei titoli posseduti da un cliente (`COD_DOSSIER`). Le posizioni e i controvalori si calcolano per dossier. |
| **Elaborazione** | Una esecuzione di un flusso per una banca e una data, registrata in [`DC_LOG_ELABORAZIONI`](oggetti/DC_LOG_ELABORAZIONI.md) con il suo `ID_ELABORAZIONE`. |
| **Entrate / uscite** | Somma dei movimenti che fanno entrare (segno +) o uscire (segno −) denaro dal conto nel mese. |
| **Estratto conto** | Il riepilogo mensile di un conto: saldo iniziale, entrate, uscite, saldo finale. Lo produce [`DC_FT_SALDI_MENSILI`](oggetti/DC_FT_SALDI_MENSILI.md). |
| **FONTE_A** | Il sistema fonte (inventato) che invia il file giornaliero dei movimenti. |
| **FONTE_B / FONTE_C** | I sistemi fonte (inventati) che inviano, rispettivamente, il file giornaliero degli ordini eseguiti e quello dei prezzi di chiusura. |
| **INTERVAL (partizioni)** | Opzione Oracle che crea da sola la partizione di un nuovo mese al primo record. I nomi generati sono di sistema, per questo si usa `TRUNCATE SUBPARTITION FOR (…)`. |
| **ISIN** | Il codice che identifica un titolo (`COD_TITOLO`). Nella demo i codici sono inventati e cominciano per `ZZ`. Vedi [`DI_DIM_TITOLO`](oggetti/DI_DIM_TITOLO.md). |
| **Istituto** | Banca a cui appartengono i dati, identificata da `COD_ISTITUTO` (codice a 5 cifre, solo valori fittizi `99xxx`). È la chiave con cui i flussi girano per un singolo istituto (`-i <ISTITUTO>`). |
| **Movimento** | Una singola operazione su un conto, con importo, causale, data contabile e data valuta: [`DC_FT_MOVIMENTI`](oggetti/DC_FT_MOVIMENTI.md). |
| **Nota di oggetto** | File `.md` accanto al sorgente, scritto a mano e facoltativo: contiene solo il perché delle scelte e le avvertenze. Compare dentro la scheda. Vedi [come documentare](come_documentare.md). |
| **Oggetto condiviso** | Oggetto definito in un motore e usato anche da un altro: semaforo, log e package di elaborazione di DEMO_CONTI sono usati anche da DEMO_INVESTIMENTI. La scheda mostra gli impatti verso i flussi di entrambi i motori. |
| **Opzione `-f`** | Opzione delle shell che salta il semaforo ("forza" il lancio). Richiede la data esatta con `-d`. |
| **Ordine** | Un acquisto o una vendita di titoli già eseguita, con dossier, titolo, quantità e prezzo: [`DI_STG_ORDINI`](oggetti/DI_STG_ORDINI.md). |
| **Posizione** | Quanti titoli ci sono in un dossier a fine giornata: posizione iniziale + acquisti − vendite = posizione finale. Vedi [`DI_FT_POSIZIONI`](oggetti/DI_FT_POSIZIONI.md). |
| **Prezzo di chiusura** | Il prezzo di un titolo a fine giornata, dal file di `FONTE_C`: [`DI_STG_PREZZI`](oggetti/DI_STG_PREZZI.md). |
| **Prezzo riportato** | Prezzo dell'ultimo giorno disponibile usato al posto di quello del giorno, che mancava. La riga è marcata con `FLG_PREZZO_RIPORTATO = 'S'`. |
| **Quadratura** | Controllo che due livelli di dati abbiano stessi conteggi e stessi importi: [`DC_VC_QUADRATURA`](oggetti/DC_VC_QUADRATURA.md). |
| **Saldo** | Quanto denaro c'è su un conto. Il saldo finale del mese è la somma di tutti i movimenti con segno fino all'ultimo giorno del mese. |
| **Scheda di oggetto** | Pagina generata dal codice per ogni oggetto, con struttura e analisi d'impatto: [schede di oggetto](oggetti/index.md). Non si modifica a mano. |
| **Semaforo** | Meccanismo che fa partire un flusso solo quando le sue fonti sono pronte: [`DC_CTL_SEMAFORO`](oggetti/DC_CTL_SEMAFORO.md) + [`DC_FN_SEMAFORO`](oggetti/DC_FN_SEMAFORO.md). |
| **Staging** | Area di appoggio dove i dati arrivano così come li manda la fonte: [`DC_STG_MOVIMENTI`](oggetti/DC_STG_MOVIMENTI.md). |
| **Storno** | Movimento che annulla un movimento precedente. Non si cancella nulla: si aggiunge un movimento di segno opposto, così lo storico resta vero. |
| **Regolamento di un ordine** | L'addebito (acquisto) o l'accredito (vendita) del denaro sul conto del cliente dopo un ordine eseguito. Se manca, [`DI_VC_REGOLAMENTO_ORDINI`](oggetti/DI_VC_REGOLAMENTO_ORDINI.md) dà `KO`. |
| **Titolo** | Azione, obbligazione o fondo che si può comprare e vendere. Il tipo (`AZIONE`, `OBBLIGAZIONE`, `FONDO`) è in [`DI_DIM_TITOLO`](oggetti/DI_DIM_TITOLO.md). |
| **TRUNCATE PARTITION / SUBPARTITION** | Svuotamento mirato della sola banca (e data) in lavorazione, prima del ricaricamento. |
| **Volumi giornalieri** | Controllo sul numero di movimenti del giorno rispetto alla media degli ultimi 20 giorni: sotto il 50% è `KO` (file arrivato a metà?). Vedi [`DC_VC_VOLUMI_GIORNALIERI`](oggetti/DC_VC_VOLUMI_GIORNALIERI.md). |
