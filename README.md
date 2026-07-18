# Sonda

Sonda è un tool didattico da riga di comando che trasferisce il contenuto di un
file in pacchetti ICMP Echo e ricostruisce un trasferimento Sonda a partire da
una cattura PCAP. È pensato esclusivamente per reti, host e catture di
laboratorio autorizzati.

## Requisiti

- Python 3.11 o successivo;
- `scapy`, installato dal file `requirements.txt`;
- privilegi amministrativi soltanto per la modalità di invio, perché Scapy crea
  pacchetti ICMP raw.

## Installazione

```bash
git clone https://github.com/MarcoSoffia/Sonda.git
cd Sonda
python3 -m pip install -r requirements.txt

python3 src/main.py --help
```

> [!IMPORTANT]
> Se usi un ambiente virtuale, per la modalità di invio esegui l'interprete
> dell'ambiente virtuale anche con `sudo`; altrimenti Python potrebbe cercare
> Scapy nell'installazione globale e non trovarlo.
>
> ```bash
> sudo .venv/bin/python3 src/main.py --send ./documento.pdf --address 192.168.1.10
> ```
>
> La modalità `--read` non richiede privilegi amministrativi e può essere
> eseguita normalmente:
>
> ```bash
> .venv/bin/python3 src/main.py --read ./cattura.pcap
> ```

## Uso

### Invio

```bash
sudo python3 src/main.py \
  --send ./documento.pdf \
  --address 192.168.1.10 \
  --strategy redundant \
  --repeat 3
```

`--send FILE` e `--read PCAP` sono mutuamente esclusivi. Con `--send` è sempre
obbligatorio `--address ADDRESS`.

Le strategie disponibili sono:

- `redundant` (predefinita): invia ogni pacchetto consecutivamente `N` volte;
- `interleaved`: invia l'intera sequenza di pacchetti per `N` cicli.

### Lettura di una cattura

```bash
python3 src/main.py --read ./cattura.pcap
```

La modalità di lettura analizza soltanto pacchetti ICMP con payload `Raw`, cerca
il primo trasferimento Sonda completo e valido e salva il risultato nella
directory corrente con nome `received_<nome-file-originale>`. Prima del
salvataggio verifica sia la dimensione sia l'hash SHA-256 dichiarati nei
metadati.

Se la cattura non contiene un trasferimento completo, se mancano sequenze o se
l'hash non coincide, il comando termina con un errore e non produce il file
ricostruito.

## Limiti attuali

- Sono accettati solo file non vuoti.
- Non sono presenti cifratura, autenticazione, ritrasmissione o un server in
  ascolto: la ricezione lavora su un file PCAP già catturato.
- Il reader ricostruisce il primo flusso Sonda completo trovato nella cattura.

Per dettagli su protocollo, classi e flussi interni, consulta il
[manuale tecnico](docs/manuale-tecnico.md).
