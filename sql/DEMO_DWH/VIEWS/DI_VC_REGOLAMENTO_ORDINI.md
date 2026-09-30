### Perché

Un ordine eseguito deve avere il suo addebito (acquisto) o accredito (vendita)
sul conto del cliente. Se l'ordine c'è ma il movimento no, il cliente ha
comprato titoli senza pagarli, o li ha venduti senza incassare: è un problema
per il cliente, che vede un saldo sbagliato, e per la banca, che ha dato i titoli
senza ricevere il denaro (o il contrario). Questa vista è il controllo che lo
scopre il giorno stesso.

È l'unico punto in cui i due motori si toccano: gli ordini sono di
`DEMO_INVESTIMENTI`, i movimenti dei conti di `DEMO_CONTI`.

### Come leggere gli esiti

- `KO`: manca il movimento con lo stesso istituto, conto, giorno, importo e la
  causale giusta (`ACQUISTO_TITOLI` per un acquisto, `VENDITA_TITOLI` per una
  vendita). Un importo diverso di un solo centesimo dà `KO`.
- `OK`: il movimento c'è.
- Un ordine senza conto di addebito dà sempre `KO`: non c'è dove cercare.

### Attenzione

- Lo staging contiene solo l'ultimo giorno caricato: la vista controlla solo
  quel giorno. Per un giorno passato serve rilanciare il carico degli ordini.
- Se i movimenti di un giorno non sono ancora stati caricati da `DEMO_CONTI`,
  tutti gli ordini di quel giorno risultano `KO` anche se l'addebito esiste nel
  sistema fonte. Prima di segnalare un problema controllare che il flusso dei
  movimenti sia girato.
- L'importo dell'ordine è quantità per prezzo; per le obbligazioni si divide per
  100, come nei controvalori mensili. Un titolo assente da `DI_DIM_TITOLO` è
  trattato come non obbligazione.
- Due ordini identici (stesso conto, giorno e importo) si accontentano di un
  solo movimento: il controllo non li conta uno a uno.
- Chi cambia il modo di registrare acquisti e vendite di titoli nei movimenti
  (causali, segno, data contabile) deve avvisare chi legge questa vista.

### Query utili

```sql
SELECT *
  FROM DEMO_DWH.DI_VC_REGOLAMENTO_ORDINI
 WHERE ESITO = 'KO'
 ORDER BY COD_ISTITUTO, COD_CONTO_ADDEBITO;
```
