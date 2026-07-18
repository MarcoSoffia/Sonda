# Manuale tecnico

Questo documento descrive l'implementazione attuale di Sonda. I nomi di classi,
opzioni e formati riportati qui corrispondono al codice in `src/`.

## Avvio e interfaccia CLI

L'applicazione non è ancora distribuita come pacchetto Python. Dalla radice del
repository si avvia con:

```bash
python3 src/main.py --help
```

La CLI, definita in `src/helper.py`, ha due modalità mutuamente esclusive:

| Opzione | Significato |
| --- | --- |
| `-s FILE`, `--send FILE` | legge e invia un file; richiede `--address` |
| `-r PCAP`, `--read PCAP` | ricostruisce il primo trasferimento Sonda valido da una cattura |
| `-a ADDRESS`, `--address ADDRESS` | destinazione IPv4/hostname per l'invio |
| `-st`, `--strategy` | `redundant` (predefinita) oppure `interleaved` |
| `-n N`, `--repeat N` | numero positivo di ripetizioni o cicli; valore predefinito 3 |

`src/main.py` sceglie la strategia, crea il mittente oppure il reader e
presenta a terminale il risultato. L'invio richiede privilegi per usare ICMP
raw; la lettura di un PCAP no.

## Componenti

| Componente | Responsabilità effettiva |
| --- | --- |
| `Chunker` | divide bytes non vuoti in chunk della dimensione richiesta |
| `Frame` | classe base con il codice di tipo `0x00` (hash) o `0x01` (dati) |
| `HashFrame` | contiene nome file, dimensione, numero e dimensione dei chunk, sessione e SHA-256 |
| `DataFrame` | contiene un singolo chunk di bytes |
| `Codec` | serializza e deserializza i frame applicativi |
| `PacketBuilder` | costruisce `IP / ICMP / Raw` tramite Scapy |
| `TransmissionStrategy` | interfaccia astratta per pianificare l'ordine dei pacchetti |
| `RedundantStrategy` | ripete ogni pacchetto prima di passare al successivo |
| `InterleavedStrategy` | ripete l'intera lista di pacchetti per più cicli |
| `SenderEngine` | prepara frame e pacchetti, applica la strategia e li invia |
| `PcapReader` | estrae da un PCAP le triple `(icmp_id, icmp_seq, raw_payload)` |
| `Reader` | individua una sessione Sonda candidata e la passa al riassemblaggio |
| `Reassembler` | valida sequenze e metadati e restituisce i chunk ordinati |

Non fanno parte dell'implementazione corrente classi separate chiamate
`MetaData`, `IntegrityService`, `PacketFilter`, `PacketClassifier`,
`ReceiverEngine` o `Report`.

## Formato dei frame e protocollo

Il mittente legge il file come bytes. `Chunker` lo divide in blocchi da 1471
byte, valore fissato da `main.py`. I dati non vengono convertiti in Base64.

```text
HashFrame iniziale (seq 0)
DataFrame dei chunk (seq 1 .. n_chunks)
HashFrame finale   (seq n_chunks + 1)
```

`HashFrame` calcola SHA-256 sul file originale e verifica che il numero di
chunk dichiarato sia coerente con dimensione del file e chunk size. Il suo
payload serializzato è:

```text
0x00 | "SONDA" | 0x01 | JSON UTF-8
```

Il byte `0x01` dopo `SONDA` è la versione di protocollo corrente. Il JSON
contiene esattamente `filename`, `file_size`, `n_chunks`, `chunk_size`,
`sha256` e `session_id`.

Un `DataFrame` è invece serializzato senza JSON:

```text
0x01 | chunk grezzo
```

`PacketBuilder` inserisce ogni payload in `Raw.load` e crea un pacchetto
`IP(dst=...) / ICMP(id=session_id, seq=sequenza) / Raw(load=payload)`.

## Flusso di invio

```text
file
  -> Path.read_bytes()
  -> Chunker
  -> HashFrame + DataFrame + HashFrame
  -> Codec.serialize()
  -> PacketBuilder.build_packet()
  -> TransmissionStrategy.plan()
  -> scapy.send()
```

`SenderEngine` genera un `icmp_id` casuale compreso tra 1 e 65535 se non ne
riceve uno. Costruisce prima tutti i pacchetti e soltanto dopo istanzia la
strategia selezionata dalla CLI.

## Gerarchia e polimorfismo

La gerarchia significativa del progetto è quella delle strategie di
trasmissione:

```text
TransmissionStrategy (ABC)
├── RedundantStrategy
└── InterleavedStrategy
```

La base riceve una lista non vuota di pacchetti e dichiara il metodo astratto
`plan()`. Entrambe le sottoclassi chiamano `super().__init__(packets)` e ne
ridefiniscono il comportamento:

```text
RedundantStrategy([A, B], repeat=2).plan()  -> [A, A, B, B]
InterleavedStrategy([A, B], cycles=2).plan() -> [A, B, A, B]
```

`SenderEngine` riceve una classe che implementa `TransmissionStrategy`, crea
l'istanza e invoca solo `strategy.plan()`: non deve conoscere quale sottoclasse
concreta sta usando. Questo è il punto in cui il polimorfismo viene usato nel
flusso applicativo.

Esiste anche la gerarchia `Frame -> DataFrame` e `Frame -> HashFrame`. Qui il
genitore centralizza la validazione del codice di tipo e le sottoclassi usano
`super()` per inizializzarlo.

## Flusso di lettura e controlli di integrità

```text
PCAP
  -> PcapReader.read()
  -> Reader: selezione di un HashFrame iniziale Sonda
  -> tutti i pacchetti con lo stesso ICMP.id
  -> Reassembler.reassemble()
  -> bytes ordinati + HashFrame
  -> controllo dimensione e SHA-256 in main.py
  -> received_<filename>
```

`PcapReader` ignora i pacchetti privi di layer ICMP o `Raw`. `Reader` considera
un candidato soltanto se ha sequenza 0, firma `SONDA`, versione supportata e
un `session_id` interno uguale all'`ICMP.id`.

`Reassembler` deduplica pacchetti con stessa sequenza e stesso payload, ma
rifiuta payload in conflitto. Richiede tutte e sole le sequenze da `0` a
`n_chunks + 1`, controlla che i due `HashFrame` abbiano gli stessi metadati e
che ogni `DataFrame` abbia la dimensione prevista. Restituisce il numero di
pacchetti unici, il `HashFrame` iniziale e la lista di chunk ordinati.

Infine `main.py` concatena i chunk, confronta dimensione e SHA-256 con i
metadati e salva il risultato solo se entrambi i controlli riescono.

## Limiti tecnici attuali

- Il protocollo trasporta dati in chiaro: non offre cifratura né autenticazione.
- Non vengono implementati retry, controllo di flusso o correzione degli errori.
- Il reader sceglie il primo trasferimento completo e valido nella cattura.
- I file vuoti sono rifiutati dalle validazioni di `Chunker` e `HashFrame`.
