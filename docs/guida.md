# Guida all'uso di TopicResearcher

## Cosa fa

TopicResearcher raccoglie materiale su un argomento e prepara proposte di ricerca associate a
una specifica istanza Life. Le proposte possono poi essere consultate per istanza.

Il catalogo ricercabile di pagine e siti non è ancora disponibile: il catalogatore deve essere
recuperato dal PC di casa.

## Come si apre

In sviluppo, avvia il backend e apri:

- servizio: <http://127.0.0.1:10052>
- documentazione interattiva delle API: <http://127.0.0.1:10052/docs>

TopicResearcher non è ancora in produzione.

## Casi d'uso

### 1. Elencare le istanze disponibili

```bash
curl http://127.0.0.1:10052/api/instances
```

Scegli un `id` con `status` uguale a `ok` e usalo negli esempi successivi.

### 2. Leggere le ricerche di un'istanza

```bash
curl --get http://127.0.0.1:10052/api/research \
  --data-urlencode "instance=<id-istanza>"
```

Senza il parametro `instance`, la stessa rotta restituisce le ricerche di tutte le istanze.

### 3. Avviare una ricerca tramite API

```bash
curl -X POST http://127.0.0.1:10052/api/research \
  -H 'Content-Type: application/json' \
  -d '{"topic":"pompe di calore","instance":"<id-istanza>","obiettivo":"confrontare costi e consumi"}'
```

`instance` è obbligatorio. Una richiesta accettata risponde con stato HTTP `202` e i dati del
processo avviato.

### 4. Avviare una ricerca da terminale

```bash
python -m suite_learn_core research "pompe di calore" \
  --node topicResearcher --instance <id-istanza>
```

## Servizi LLM

Oggi TopicResearcher non chiama direttamente i modelli. La ricerca passa dal package condiviso
`suite_learn_core`; i modelli si cambiano nel file `llm-routing.json` dell'istanza.

## Problemi comuni

- **`instance_required`**: manca `instance` nel corpo del `POST /api/research`.
- **`instance_unknown`**: l'ID indicato non è registrato. Ripeti `GET /api/instances` e usa uno
  degli ID restituiti.
- **Istanza non raggiungibile**: scegli un'istanza con `status: "ok"`; una scrittura verso
  un'istanza non raggiungibile restituisce `instance_unreachable`.
- **Catalogo assente**: è previsto, ma non è ancora disponibile perché il catalogatore deve
  essere recuperato dal PC di casa.
