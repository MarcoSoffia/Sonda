# Scelte implementative

La classe astratta `TransmissionStrategy` definisce gli elementi comuni a tutte
le strategie: riceve una lista di pacchetti, ne verifica la validità e dichiara
il metodo astratto `plan()`. Questo metodo stabilisce l’ordine con cui i
pacchetti devono essere inviati.

Le classi `RedundantStrategy` e `InterleavedStrategy` ereditano da
`TransmissionStrategy` perché rappresentano due tipi diversi della stessa
entità. In altre parole, una `RedundantStrategy` è una strategia di
trasmissione e una `InterleavedStrategy` è una strategia di trasmissione.

Abbiamo preferito l’ereditarietà a due funzioni perché le strategie
condividono uno stato e un comportamento comune, ma devono poter specializzare
la pianificazione dei pacchetti. Questa struttura consente inoltre di aggiungere
in futuro nuove modalità, come una `ParityStrategy`, creando una nuova
sottoclasse e implementando `plan()` senza modificare la logica di
`SenderEngine`.

La composizione viene comunque utilizzata tra `SenderEngine` e la strategia:
il sender usa una strategia, ma non eredita da essa, perché un sender non è una
strategia. L’ereditarietà viene invece applicata soltanto tra
`TransmissionStrategy` e le sue specializzazioni.