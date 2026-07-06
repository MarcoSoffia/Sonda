# Sonda - TODO

> Roadmap di implementazione del progetto Sonda (ICMP Exfiltration Tool).
> Aggiornare lo stato dei task man mano che si procede.

---

## Fase 1 — Data Model e Servizi di Base

- [x] Creare `src/frame.py`: classi `Frame` (ABC), `DataFrame` (payload bytes), `HashFrame` (file bytes + digest SHA-256)
- [x] Creare `src/chunker.py`: classe `Chunker` (split file in chunk di dimensione fissa)
- [x] Creare `src/codec.py`: classe `Codec` (`bytetostr`, `strtobyte`, `serialize`, `deserialize`)
- [x] Creare `src/main.py`: CLI base con `--send` e `--read`
- [x] Creare `tests/test_frame.py`: test validazione tipi, costruttori
- [x] Creare `tests/test_chunker.py`: test chunking, validazione parametri
- [x] Creare `tests/test_codec.py`: test serializzazione/deserializzazione
- [x] Creare `src/helper.py`: per la gestione corretta dei messaggi e argomenti

---

## Fase 2 — Packet Building e Strategia

- [x] Creare `src/packet_builder.py`: classe `PacketBuilder` (costruisce pacchetti ICMP con IP/ICMP/Raw)
- [ ] Creare `src/strategy.py`: classe astratta `TransmissionStrategy` (metodo `plan(frames)`)
- [ ] Creare `src/strategy.py`: classe `RedundantStrategy` (ripete ogni frame N volte)
- [ ] Creare `src/strategy.py`: classe `InterleavedStrategy` (ripete l'intero ciclo N volte)

---

## Fase 3 — Sender Engine

- [ ] Creare `src/sender.py`: classe `SenderEngine` (coordina FileReader → Chunker → IntegrityService → Codec → Frame → Strategy → PacketBuilder → invio)
- [ ] Aggiornare `src/main.py`: CLI completa per modalità send (`--send --file X --remote Y --strategy Z --repeat N`)
- [ ] Rinominare `src/Chunker.py` → `src/chunker.py` (snake_case)

---

## Fase 4 — Receiver Engine

- [ ] Creare `src/pcap_reader.py`: classe `PcapReader` (legge file .pcap con Scapy)
- [ ] Creare `src/packet_filter.py`: classe `PacketFilter` (filtra pacchetti per session_id)
- [ ] Creare `src/packet_classifier.py`: classe `PacketClassifier` (classifica META/DATA dal primo byte di Raw.load)
- [ ] Creare `src/reassembler.py`: classe `Reassembler` (ordina chunk, deduplica, ricostruisce file, rileva buchi)
- [ ] Creare `src/receiver.py`: classe `ReceiverEngine` (coordina PcapReader → PacketFilter → PacketClassifier → Reassembler → IntegrityService → report)
- [ ] Aggiornare `src/main.py`: CLI completa per modalità read (`--read cattura.pcap --output file_out`)

---

## Fase 5 — Refinement e Test

- [ ] Test end-to-end: invia file → cattura pcap → ricostruisci → verifica SHA-256
- [ ] Aggiungere logging e progress bar
- [ ] Validazione input e gestione errori di rete
- [ ] Implementare `ParityStrategy` (opzionale)
- [ ] Aggiornare `docs/scelte.md` con decisioni implementative
- [ ] Aggiornare `docs/devlog.md` con progresso
- [ ] Creare `src/__init__.py`
