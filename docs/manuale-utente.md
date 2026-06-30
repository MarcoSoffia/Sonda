# Manuale utente

# Manuale utente

Sonda è un tool da laboratorio che permette di inviare e ricostruire dati attraverso pacchetti ICMP Echo. Il programma lavora dividendo un file in chunk, inserendoli nel payload ICMP e ricostruendoli successivamente a partire da una cattura `.pcap`.

Il progetto è pensato solo per ambienti controllati, reti proprie o scenari didattici autorizzati.

## Installazione

Clonare la repository:

```bash
git clone https://github.com/MarcoSoffia/Sonda.git
cd Sonda
```

Installare le dipendenze:

```bash
pip install -r requirements.txt
```

Il tool usa Scapy, quindi per l’invio reale di pacchetti ICMP può essere necessario eseguire il programma con privilegi di amministratore/root.

## Avvio

Per vedere le opzioni disponibili:

```bash
python -m sonda --help
```

## Invio di un file

Per inviare un file verso un host remoto:

```bash
sudo python -m sonda --send --file file.txt --remote 192.168.1.10
```

Parametri principali:

* `--send`: avvia la modalità di invio;
* `--file`: indica il file da leggere e dividere in chunk;
* `--remote`: indica l’indirizzo IP del destinatario.

Durante l’invio, il programma legge il file come bytes, lo divide in chunk, crea i frame META/DATA e li trasforma in pacchetti ICMP. I frame META contengono informazioni come numero di chunk, dimensione del file e hash SHA-256; i frame DATA contengono i chunk grezzi del file.

## Lettura da file PCAP

Per ricostruire un file partendo da una cattura di rete:

```bash
sudo python -m sonda --read cattura.pcap
```

Parametri principali:

* `--read`: avvia la modalità di lettura;
* `cattura.pcap`: file di cattura contenente i pacchetti ICMP da analizzare.

Il reader legge i pacchetti dal file `.pcap`, filtra quelli appartenenti alla stessa sessione, distingue i frame META dai frame DATA, elimina eventuali duplicati e prova a ricostruire il file originale.

## Esempio completo

1. Su una macchina, preparare un file:

```bash
echo "Messaggio di test" > file.txt
```

2. Avviare una cattura del traffico ICMP con uno strumento come Wireshark o tcpdump.

3. Inviare il file:

```bash
sudo python -m sonda --send --file file.txt --remote 192.168.1.10
```

4. Salvare la cattura come `cattura.pcap`.

5. Ricostruire il contenuto:

```bash
sudo python -m sonda --read cattura.pcap
```
# Manuale utente

Sonda è un tool da laboratorio che permette di inviare e ricostruire dati attraverso pacchetti ICMP Echo. Il programma lavora dividendo un file in chunk, inserendoli nel payload ICMP e ricostruendoli successivamente a partire da una cattura `.pcap`.

Il progetto è pensato solo per ambienti controllati, reti proprie o scenari didattici autorizzati.

## Installazione

Clonare la repository:

```bash
git clone https://github.com/MarcoSoffia/Sonda.git
cd Sonda
```

Installare le dipendenze:

```bash
pip install -r requirements.txt
```

Il tool usa Scapy, quindi per l’invio reale di pacchetti ICMP può essere necessario eseguire il programma con privilegi di amministratore/root.

## Avvio

Per vedere le opzioni disponibili:

```bash
python -m sonda --help
```

## Invio di un file

Per inviare un file verso un host remoto:

```bash
sudo python -m sonda --send --file file.txt --remote 192.168.1.10
```

Parametri principali:

* `--send`: avvia la modalità di invio;
* `--file`: indica il file da leggere e dividere in chunk;
* `--remote`: indica l’indirizzo IP del destinatario.

Durante l’invio, il programma legge il file come bytes, lo divide in chunk, crea i frame META/DATA e li trasforma in pacchetti ICMP. I frame META contengono informazioni come numero di chunk, dimensione del file e hash SHA-256; i frame DATA contengono i chunk grezzi del file.

## Lettura da file PCAP

Per ricostruire un file partendo da una cattura di rete:

```bash
sudo python -m sonda --read cattura.pcap
```

Parametri principali:

* `--read`: avvia la modalità di lettura;
* `cattura.pcap`: file di cattura contenente i pacchetti ICMP da analizzare.

Il reader legge i pacchetti dal file `.pcap`, filtra quelli appartenenti alla stessa sessione, distingue i frame META dai frame DATA, elimina eventuali duplicati e prova a ricostruire il file originale.

## Esempio completo

1. Su una macchina, preparare un file:

```bash
echo "Messaggio di test" > file.txt
```

2. Avviare una cattura del traffico ICMP con uno strumento come Wireshark o tcpdump.

3. Inviare il file:

```bash
sudo python -m sonda --send --file file.txt --remote 192.168.1.10
```

4. Salvare la cattura come `cattura.pcap`.

5. Ricostruire il contenuto:

```bash
sudo python -m sonda --read cattura.pcap
```

## Output atteso

Al termine dell’invio o della lettura, il programma dovrebbe mostrare un report con informazioni come:

* numero totale di frame/pacchetti gestiti;
* eventuali duplicati trovati;
* eventuali chunk mancanti;
* durata dell’operazione;
* esito della verifica di integrità tramite SHA-256.

Se l’hash del file ricostruito coincide con quello indicato nel META, la ricostruzione viene considerata corretta.

## Errori comuni

### Permessi insufficienti

L’invio di pacchetti ICMP raw può richiedere privilegi elevati.

Soluzione:

```bash
sudo python -m sonda --send --file file.txt --remote 192.168.1.10
```

### File non trovato

Succede quando il percorso passato a `--file` o `--read` non esiste.

Controllare il nome del file e il percorso usato nel comando.

### Host remoto non raggiungibile

Verificare che l’indirizzo IP sia corretto e che la rete permetta traffico ICMP.

### Ricostruzione incompleta

Può succedere se nella cattura mancano pacchetti DATA o META. In questo caso il report indica i chunk mancanti e l’integrità potrebbe risultare non valida.

## Note di utilizzo

Il programma deve essere usato solo in laboratorio o in reti dove si ha autorizzazione esplicita. Non è pensato per traffico reale non autorizzato o per aggirare controlli di sicurezza.

## Output atteso

Al termine dell’invio o della lettura, il programma dovrebbe mostrare un report con informazioni come:

* numero totale di frame/pacchetti gestiti;
* eventuali chunk mancanti;
* durata dell’operazione;
* esito della verifica di integrità tramite SHA-256.

Se l’hash del file ricostruito coincide con quello indicato nel META, la ricostruzione viene considerata corretta.

## Errori comuni

### Permessi insufficienti

L’invio di pacchetti ICMP raw può richiedere privilegi elevati.

Soluzione:

```bash
sudo python -m sonda --send --file file.txt --remote 192.168.1.10
```

### File non trovato

Succede quando il percorso passato a `--file` o `--read` non esiste.

Controllare il nome del file e il percorso usato nel comando.

### Host remoto non raggiungibile

Verificare che l’indirizzo IP sia corretto e che la rete permetta traffico ICMP.

### Ricostruzione incompleta

Può succedere se nella cattura mancano pacchetti DATA o META. In questo caso il report indica i chunk mancanti e l’integrità potrebbe risultare non valida.

## Note di utilizzo

Il programma deve essere usato solo in laboratorio o in reti dove si ha autorizzazione esplicita. Non è pensato per traffico reale non autorizzato o per aggirare controlli di sicurezza.

