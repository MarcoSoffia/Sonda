
### Architettura generale

Il programma è diviso in due flussi principali:

Sender flow:

file originale
  -> FileReader
  -> Chunker
  -> Frame META/DATA/END
  -> TransmissionStrategy
  -> PacketBuilder
  -> Sender
  -> rete / pacchetti ICMP
Reader flow:

file .pcap
  -> PcapReader
  -> PacketFilter
  -> PacketClassifier
  -> FrameCollection
  -> Reassembler
  -> IntegrityService
  -> file ricostruito + report

### Responsabilità

| Blocco        | Cosa riceve             | Cosa produce                 | Errori da gestire                      |
| ------------- | ----------------------- | ---------------------------- | -------------------------------------- |
| FileReader    | path file               | bytes                        | file inesistente, permessi             |
| Chunker       | bytes, chunk size       | lista di chunk               | chunk size non valido                  |
| Frame         | tipo + metadata/payload | oggetto logico META/DATA/END | campi mancanti, tipo non valido        |
| Strategy      | lista Frame             | ordine di invio              | repeat negativo, strategia sconosciuta |
| PacketBuilder | Frame                   | pacchetto ICMP               | payload troppo grande                  |
| Sender        | pacchetti               | invio reale                  | permessi root, rete non raggiungibile  |

### Tipo del dato attraverso il programma

file.txt -> bytes -> chunk bytes -> Frame DATA -> Raw.load del pacchetto ICMP

Internamente il programma lavora con bytes, perché i file devono essere trattati come dati binari e non come stringhe. Anche se l'esempio usa file.txt, questa scelta permette in futuro di supportare anche altri tipi di file, come immagini, archivi o file binari.

I chunk del file restano bytes grezzi fino al pacchetto ICMP. Per i pacchetti DATA non viene creato un JSON e non viene usato Base64: il chunk viene copiato direttamente nel campo `Raw.load`.

Il JSON serve solo per il pacchetto META, dove il payload contiene metadati piccoli e testuali, ad esempio:

- numero totale di chunk;
- chunk size;
- hash SHA-256 del file originale;
- nome file opzionale;
- dimensione totale del file;
- versione del formato.

Questa scelta evita overhead inutile sui dati veri: Base64 aumenterebbe la dimensione dei chunk e renderebbe il traffico meno vicino al modello scelto, dove `Raw.load` contiene direttamente bytes grezzi.

### Grandezza payload

La dimensione del chunk deve essere scelta in modo che il pacchetto ICMP finale resti entro un limite gestibile dalla rete e dagli strumenti usati per generarlo.

Il limite pratico dipende da MTU, header IP, header ICMP ed eventuali vincoli della libreria. Il `PacketBuilder` deve quindi validare che `Raw.load` non sia troppo grande prima dell'invio.

All'inizio possiamo usare una costante di configurazione, ad esempio `CHUNK_SIZE`, e riportarla nel META per permettere al receiver di verificare che i chunk ricevuti siano coerenti.

### Perché ereditarietà?

Una RedundantStrategy è una *TransmissionStrategy*.
Una InterleavedStrategy è una *TransmissionStrategy*.

Tutte le strategie condividono lo stesso scopo generale: ricevono una lista di frame e producono un piano di invio. Cambia però il modo in cui questo piano viene costruito.

Per questo una gerarchia di classi è adatta:

la classe base definisce l'interfaccia comune;
le sottoclassi implementano comportamenti diversi;
il sender può usare il polimorfismo;
nuove strategie possono essere aggiunte senza riscrivere il motore principale.


### Gestione dei duplicati e dei chunk mancanti

### Duplicati
Se lo stesso `ICMP.id` e lo stesso `ICMP.seq` vengono ricevuti più volte, il reassembler conserva una sola copia del chunk.

Esempio:

ricevuti: 4, 4, 5, 5, 6, 6
usati:    4, 5, 6

#### Chunk mancanti
Per i chunk mancanti facciamo un report dal receiver.

Il receiver usa il META per sapere quanti chunk deve aspettarsi. Se i DATA usano `ICMP.seq` da 4 in poi, il primo chunk corrisponde a `seq = 4`, il secondo a `seq = 5`, e così via. Un buco nella sequenza indica un chunk mancante.

#### Verifica di integrità

L'integrità viene verificata con un hash del file originale.

Sender:
file originale -> SHA-256 -> pacchetto META

Reader:
file ricostruito -> SHA-256 -> confronto con hash dichiarato nel META

### Quindi:
`ICMP.id`  = `session_id`
`ICMP.seq` = numero logico del pacchetto
`Raw.load` = dati grezzi oppure piccolo pacchetto META

META  -> descrive la trasmissione, quindi hash, numero di chunk, chunk size, dimensione totale, versione del formato
DATA  -> contiene chunk grezzo del file
END   -> opzionale, conferma fine stream / hash finale

Usiamo convenzioni opzionali su `ICMP.seq`:
`ICMP.seq = 1, 2, 3`       -> META
`ICMP.seq = 4..65531`      -> DATA
`ICMP.seq = 65533..65535`  -> END opzionale

Esempio:
META:
`ICMP.id`  = `session_id`
`ICMP.seq` = `1`
`Raw.load` = JSON compatto con metadati (`n_chunks`, `chunk_size`, `file_size`, `sha256`)

DATA:
`ICMP.id`  = `session_id`
`ICMP.seq` = `chunk_seq`
`Raw.load` = bytes grezzi del chunk

Il primo chunk DATA usa `chunk_seq = 4`. L'indice logico del chunk si può ricavare con `chunk_index = ICMP.seq - 4`.

END / META di nuovo per finire:
`ICMP.id`  = `session_id`
`ICMP.seq` = `65535`
`Raw.load` = END


## Considerazioni di detection

Un traffico ICMP usato per trasportare dati può essere rilevato da firewall, IDS o sistemi di monitoraggio tramite diversi indicatori:

- payload ICMP più grande del normale;
- alto numero di Echo Request verso la stessa destinazione;
- uso ripetuto dello stesso `ICMP.id`;
- `ICMP.seq` progressivo e coerente con una trasmissione dati;
- payload ad alta entropia o molto variabile;
- assenza di un rapporto normale tra Echo Request ed Echo Reply;
- presenza di metadati riconoscibili nel payload, come il pacchetto META.

Per rendere il laboratorio più realistico, il tool ad un certo punto dovrà permettere di configurare chunk size, ridondanza e rate di invio (Magari inizialmente solo da costanti in cima alla classe).

#### balancer

web server + DNS + ICMp + 