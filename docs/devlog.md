# Devlog

Registro delle consegne ricostruito dalla cronologia Git (28 giugno–19 luglio 2026).

## Settimana 1 — Analisi, progettazione e scaffolding (28–29 giugno)


- Redazione della proposta e della prima roadmap tecnica.
- Predisposizione della repository: `.gitignore`, `README`, dipendenza `scapy` e struttura `src/`, `docs/` e `tests/`.
- Produzione della documentazione iniziale: manuale utente, manuale tecnico, scelte progettuali e note sull'uso dell'IA.
- Creazione dei primi diagrammi UML, incluso il diagramma di sequenza dell'invio e il diagramma generale del sistema.

## Settimana 2 — Nucleo del protocollo e primi test (30 giugno–6 luglio)


- Implementazione di `Chunker` per dividere un file in chunk.
- Definizione e correzione della gerarchia `Frame`; aggiunta del supporto iniziale alla deserializzazione.
- Implementazione di `Codec` per serializzare e deserializzare i frame lavorando direttamente su `bytes`, evitando l'overhead della conversione in stringhe.
- Implementazione ed evoluzione di `PacketBuilder` per costruire i pacchetti ICMP.
- Estrazione della gestione degli argomenti CLI in `helper.py`, con opzioni per invio, lettura e help.
- Introduzione di `TransmissionStrategy` e della strategia `RedundantStrategy`.
- Aggiunta e correzione dei test di base per chunker, frame e codec; aggiornamento del file `TODO` e della documentazione di supporto.

## Settimana 3 — Motore di invio e prima lettura da PCAP (7–13 luglio)

- Implementazione di `SenderEngine` e collegamento al punto di ingresso dell'applicazione.
- Correzione degli argomenti della CLI necessari all'invio.
- Prima implementazione di `Reader` per leggere una cattura PCAP e produrre una ricostruzione iniziale del file.
- Aggiunta di un file PCAP e di un file ricevuto di esempio per la verifica manuale del flusso.

## Settimana 4 — Strategie, metadati e validazione della ricezione (14–18 luglio)


- Implementazione di `InterleavedStrategy` e integrazione nella CLI, in `main.py` e in `SenderEngine`.
- Estensione di `HashFrame` con metadati del trasferimento: nome file, numero di chunk, dimensione del chunk e identificativo di sessione.
- Aggiornamento di codec, sender e reader per trasportare e utilizzare i nuovi metadati. Introduzione di una firma in bytes.
- Rafforzamento della ricostruzione: verifica delle sequenze, dimensione del file e hash SHA-256 prima del salvataggio dell'output.
- Generazione di un identificativo di sessione casuale per ogni invio, riutilizzato come `ICMP.id` e nei metadati del trasferimento.
- Aggiunta della firma `SONDA` e della versione del protocollo ai soli `HashFrame`, per distinguere il protocollo dal traffico ICMP non pertinente.
- Aggiornamento del reader PCAP: analizza una cattura ICMP completa, ignora il noise e ricostruisce il primo flusso Sonda completo e valido rilevato.

