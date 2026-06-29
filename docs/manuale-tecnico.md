
### Architettura generale

Il programma è diviso in due flussi principali:

Sender flow:

file originale
  -> FileReader
  -> Chunker
  -> Frame META/DATA
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
| Frame         | tipo + metadata/payload | oggetto logico META/DATA      | campi mancanti, tipo non valido        |
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

Per distinguere META da DATA senza ispezionare il contenuto di `Raw.load`,
usiamo un **byte prefisso**: `0x00` per META, `0x01` per DATA.

Usiamo convenzioni opzionali su `ICMP.seq`:
`ICMP.seq = 1, 2, 3`       -> META
`ICMP.seq = 4..65531`      -> DATA
`ICMP.seq = 65533..65535`  -> META finale (chiude la trasmissione)

Esempio:
META:
`ICMP.id`  = `session_id`
`ICMP.seq` = `1`
`Raw.load` = `b'\x00'` + JSON compatto con metadati (`n_chunks`, `chunk_size`, `file_size`, `sha256`)

DATA:
`ICMP.id`  = `session_id`
`ICMP.seq` = `chunk_seq`
`Raw.load` = `b'\x01'` + bytes grezzi del chunk

Il primo chunk DATA usa `chunk_seq = 4`. L'indice logico del chunk si può ricavare con `chunk_index = ICMP.seq - 4`.


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

web server + DNS + ICMp + # Sonda — Schema astratto

## Classi e metodi

### Frame
Unità logica del sistema: META (metadati) oppure DATA (chunk del file).

```
Frame
├── tipo          # enum: META | DATA
├── seq           # int: numero sequenza ICMP
├── payload       # bytes: contenuto grezzo
├── to_bytes()    # serializza per Raw.load
└── from_bytes()  # deserializza da Raw.load
```

### MetaData
I metadati di una trasmissione. Viaggiano dentro un Frame di tipo META.

```
MetaData
├── n_chunks      # int
├── chunk_size    # int
├── file_size     # int
├── sha256        # str
├── version       # str
├── session_id    # int
├── to_json()     # str
└── from_json()   # MetaData
```

### Chunker
Taglia un file in pezzi.

```
Chunker
├── chunk_size    # int (privato)
└── chunk(bytes)  # list[bytes]
```

### Reassembler
Ricompatte i pezzi ricevuti. Il secondo META ricevuto segnala la fine.

```
Reassembler
├── chunks        # dict[int, bytes] (privato)
├── meta          # MetaData (privato)
├── meta_count    # int (privato): conta i META visti
├── add_chunk(seq, bytes)
├── set_meta(meta: MetaData)     # al primo META inizializza, al secondo chiude
├── is_complete() # bool
├── missing()     # list[int]
└── reassemble()  # bytes
```

### IntegrityService
Hash del file, prima e dopo.

```
IntegrityService
├── hash(bytes)            # str (SHA-256)
└── verify(bytes, expected) # bool
```

### Codec
Serializza / deserializza i metadati dentro il payload META.

```
Codec
├── encode(meta: MetaData)  # bytes
└── decode(data: bytes)     # MetaData
```

### PacketBuilder
Costruisce il pacchetto ICMP pronto da spedire. Unica classe che tocca Scapy.
Aggiunge un byte prefisso al payload per marcare il tipo:
`0x00` = META, `0x01` = DATA.

```
PacketBuilder
├── dst            # str (privato)
├── session_id     # int (privato)
├── build_meta(meta: MetaData)              # pacchetto, payload = b'\x00' + json
└── build_data(seq: int, chunk: bytes)      # pacchetto, payload = b'\x01' + chunk
```

### TransmissionStrategy (astratta)
Decide l'ordine di invio dei frame.

```
TransmissionStrategy (astratta)
└── plan(frames: list[Frame])  # list[Frame]
```

Sottoclassi:

```
RedundantStrategy(TransmissionStrategy)
├── repeat   # int
└── plan()   # 0,0,0, 1,1,1, 2,2,2 ...

InterleavedStrategy(TransmissionStrategy)
├── cycles   # int
└── plan()   # 0,1,2, 0,1,2, 0,1,2 ...
```

### SenderEngine
Coordina tutto il lato mittente.

```
SenderEngine
├── reader:      FileReader
├── chunker:     Chunker
├── integrity:   IntegrityService
├── codec:       Codec
├── builder:     PacketBuilder
├── strategy:    TransmissionStrategy
└── send(filepath, dst) → Report
```

### ReceiverEngine
Coordina tutto il lato ricevente.

```
ReceiverEngine
├── reader:      PcapReader
├── filter:      PacketFilter
├── classifier:  PacketClassifier
├── reassembler: Reassembler
├── integrity:   IntegrityService
├── codec:       Codec
└── receive(pcap_path) → (bytes, Report)
```

### Classi di supporto (receiver)

```
FileReader
└── read(path) → bytes

PcapReader
└── read(path) → list[pacchetto]

PacketFilter
└── by_session(pacchetti, session_id) → list[pacchetto]

PacketClassifier
├── tipo(pacchetto)      → enum     # legge Raw.load[0]: 0x00=META, 0x01=DATA
├── seq(pacchetto)       → int
└── payload(pacchetto)   → bytes    # Raw.load[1:] (salta il byte tipo)
```

### Report
Quello che restituiscono Sender e Receiver.

```
Report
├── total_frames     # int
├── duplicates       # int
├── missing_chunks   # list[int]
├── duration_sec     # float
└── integrity_ok     # bool
```

---

## Relazioni di appartenenza

```
SenderEngine
├── possiede → FileReader
├── possiede → Chunker
├── possiede → IntegrityService
├── possiede → Codec
├── possiede → PacketBuilder
└── usa       → TransmissionStrategy

ReceiverEngine
├── possiede → PcapReader
├── possiede → PacketFilter
├── possiede → PacketClassifier
├── possiede → Reassembler
├── possiede → IntegrityService
└── possiede → Codec
```

---

## Gerarchia strategie

```
TransmissionStrategy       (interfaccia)
├── RedundantStrategy      (ripete ogni frame N volte)
└── InterleavedStrategy    (ripete l'intero ciclo N volte)
```

---

## Flusso Sender

```
file.txt
  → FileReader.read()                        # bytes
  → IntegrityService.hash()                  # sha256
  → Chunker.chunk()                          # list[bytes]
  → Codec.encode(meta)                       # bytes META
  → creazione Frame:
      META iniziale + DATA[0..n] + META finale
  → TransmissionStrategy.plan()              # ordine di invio
  → PacketBuilder.build_meta() / build_data()
  → send()                                   # rete
  → Report
```

## Flusso Receiver

```
capture.pcap
  → PcapReader.read()                        # pacchetti grezzi
  → PacketFilter.by_session()                # solo la nostra sessione
  → per ogni pacchetto:
      → PacketClassifier.tipo()              # META | DATA
      → se META:
          Codec.decode() → Reassembler.set_meta()
          (primo META = inizializza, secondo META = fine trasmissione)
      → se DATA:
          Reassembler.add_chunk()
  → Reassembler.reassemble()                 # bytes
  → IntegrityService.verify()                # bool
  → (bytes, Report)
```

---

## Protocollo su ICMP

### Raw.load layout

```
┌──────┬─────────────────────────────────┐
│ 0x00 │ JSON (metadati)                 │  → META
└──────┴─────────────────────────────────┘
┌──────┬─────────────────────────────────┐
│ 0x01 │ chunk grezzo                    │  → DATA
└──────┴─────────────────────────────────┘
  byte 0     resto del payload
```

Il primo byte identifica il tipo in O(1), senza ispezionare il contenuto.

### ICMP.seq

```
seq 1..3     → META iniziale (stessi metadati, inviato ridondante)
seq 4..65531 → DATA (chunk grezzi)
seq 65532+   → META finale   (stessi metadati, chiude la trasmissione)
```

Il META iniziale e il META finale portano lo stesso contenuto.
Il receiver smette di aspettare dati quando riceve il secondo META.
