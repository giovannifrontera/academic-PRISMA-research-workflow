---
name: edtech-pilot-design
description: Usa quando occorre progettare uno studio pilota o quasi-sperimentale in ambito Ed-Tech (AI a scuola, HCI per l'apprendimento) con approccio mixed-methods. Non usare per revisioni sistematiche, studi osservazionali puri o studi già avviati.
---

# Progettazione Studio Pilota Ed-Tech (Mixed-Methods)

## Overview

Questa skill guida la progettazione rigorosa di studi pilota o quasi-sperimentali in ambito Ed-Tech (AI in classe, HCI per l'apprendimento). Produce un **Protocollo di Ricerca** strutturato, pronto per essere sottomesso, condiviso con le scuole o usato come base per un paper.

**Cos'è un pilot study** — L'obiettivo primario è la **fattibilità** (*feasibility*): verificare che gli strumenti funzionino, stimare l'effect size per dimensionare lo studio completo, rilevare problemi procedurali. L'efficacia dell'intervento è un obiettivo *secondario* nel pilot.

**Tipo di skill:** Rigida — segui le fasi nell'ordine indicato senza saltarne alcuna.

**Regola d'oro:** Non passare alla fase successiva senza conferma esplicita dell'utente. *Conta come conferma esplicita:* una risposta affermativa chiara ("sì", "ok", "procedi", "confermo"), oppure la risposta completa alle domande della fase. *Non conta:* silenzio, risposta parziale, o un semplice "capito". Se l'utente vuole saltare una fase, avvisalo che il protocollo risulterà incompleto, documenta la lacuna nel file e prosegui secondo la sua scelta.

---

## Avvio

### Contesto dello studio (prima di tutto)

Prima di qualsiasi altra verifica, identifica il contesto istituzionale:

> "Lo studio che vuoi progettare è rivolto a: (a) scuola secondaria italiana, (b) università, o (c) formazione professionale / altro contesto?"

- **Scuola secondaria** → applica tutte le raccomandazioni sul calendario MIUR, consenso informato dei genitori (GDPR minori), autorizzazione del Dirigente Scolastico.
- **Università** → adatta: niente consenso genitori, calendario accademico, maggiore probabilità di randomizzazione, soggetti adulti.
- **Altro** → chiedi dettagli prima di procedere.

Dichiara esplicitamente all'utente: *"Contesto identificato: [contesto scelto]. Adatto le raccomandazioni di conseguenza."*

---

### Ripresa di sessione (priorità assoluta)

**Prima ancora di presentare le fasi**, verifica se esistono già file prodotti da sessioni precedenti:
- Se `protocollo_ricerca.md` esiste → leggi **solo il Blocco STATO** nelle prime righe (non l'intero file). Dichiara esplicitamente: *"Ho trovato `protocollo_ricerca.md`. Ripristino il contesto dal Blocco STATO."*
- Identifica la fase corrente dal Blocco STATO e chiedi: *"Eravamo alla Fase [N]. Confermi di voler proseguire da lì?"*
- Leggi le sezioni complete del file solo quando la fase corrispondente è in esecuzione.
- Non riformulare mai decisioni già prese nelle fasi precedenti senza esplicita richiesta dell'utente

**Controlla se esiste un report PRISMA** (prodotto dalla skill `prisma-review` o creato manualmente):
- Cerca prima il file standard `prisma_synthesis.md` nella cartella corrente.
- Se non esiste, chiedi esplicitamente: *"Hai già un report di revisione sistematica (PRISMA o simile)? Se sì, indicami il nome o il percorso del file."*
- Accetta qualsiasi nome di file (es. `review_prisma_definitiva.md`, `prisma_log.md`, `sintesi_metodologica.md`, ecc.).
- Se l'utente fornisce un percorso → leggilo integralmente e trattalo come se fosse `prisma_synthesis.md`.
- Se il file esiste (qualunque nome) → leggilo subito e estrai automaticamente le sezioni "OUTPUT PER PILOT STUDY" o sezioni equivalenti:
  - **Effect size aggregati** → pre-compila il valore `d` per la power analysis in Fase 2d
  - **Framework teorici dominanti** → pre-compila la sezione Framework Teorico in Fase 1
  - **Strumenti di misura più usati** → pre-compila la scelta strumenti in Fase 3
  - **RQ non ancora investigate** → suggeriscile come domande di ricerca candidate in Fase 1
  - **Gap di popolazione** → inseriscilo nella motivazione del pilot in Fase 1
  - **Durata tipica degli interventi** → usa il range come vincolo realistico in Fase 4
- Comunica all'utente: *"Ho letto il report PRISMA (`[nome file]`). Ho pre-compilato i campi bibliografici nelle fasi pertinenti. Vuoi procedere con questi valori o preferisci inserirne di diversi?"*

**Se non esiste `protocollo_ricerca.md`**, dichiara esplicitamente: *"Nessun file di sessione precedente trovato. Parto dalla Fase 1."*

**Ingresso alternativo — dati già raccolti:** prima di procedere, chiedi:

> "Hai già raccolto i dati, o sei ancora in fase di progettazione?"

- **Progettazione** → segui il workflow completo dalla Fase 1.
- **Dati già raccolti** → salta alle Fasi già coperte e vai direttamente alla Fase 5 (Piano di Analisi) o alla Fase 6 (Results Paper). Avvisa l'utente: *"Poiché i dati sono già stati raccolti, salto le fasi di progettazione. Iniziamo dalla Fase [N]."*

---

**Controlla se esiste un database RAG** (creato dalla skill `hybrid-rag` durante una precedente `prisma-review`):
- Verifica se esiste `rag_db/` nella cartella di lavoro corrente.
- Se esiste → aggiorna il Blocco STATO con `RAG: sì` e informa l'utente: *"Trovato database RAG locale. Posso interrogarlo durante la progettazione per recuperare evidenze specifiche dalla letteratura."*
- Quando si discutono framework, strumenti o ipotesi nelle fasi successive, suggerisci query mirate: `py hybrid_rag.py query "<costrutto>" --n 3`
- Se `rag_db/` non esiste → `RAG: no` nel Blocco STATO; la progettazione si basa solo su `prisma_synthesis.md`.

**Se non viene trovato nessun report PRISMA**, chiedi:

> "Hai già condotto una revisione sistematica della letteratura (es. con PRISMA) su questo tema?"

- **Sì, ho un file** → chiedi il percorso esatto e leggilo come descritto sopra (accetta qualsiasi nome)
- **Sì, ma non ho il file** → chiedi di condividere verbalmente i risultati chiave (gap, framework, strumenti, effect size medi)
- **No, ma ho tempo per una revisione** → suggerisci di invocare prima la skill `prisma-review`. Il pilot senza revisione sistematica rischia di replicare studi già esistenti o di scegliere strumenti non validati nel contesto.
- **No, ma ho tempo per una revisione** → suggerisci di invocare prima la skill `prisma-review` tramite il tool **`Skill`** di Claude Code.
- **No, e non ho tempo per una PRISMA completa** → proponi questa alternativa leggera: *"Possiamo fare una scoping review rapida: 2-3 query mirate su Semantic Scholar + ERIC per identificare i 5-10 studi più citati sul tuo tema, estrarre framework e strumenti dominanti, e usare d=0.5 come effect size conservativo per la power analysis. Ci vogliono circa 2 ore invece di settimane. Vuoi procedere così?"* Documenta nel protocollo che la revisione è una scoping review rapida (non una revisione sistematica PRISMA) e le implicazioni per la generalizzabilità.

Poi presenta all'utente:
1. Le 6 fasi del processo (Framework → Design → Strumenti → Procedura → Analisi/Etica → Preprint)
2. I 4 file che verranno prodotti progressivamente
3. La distinzione tra obiettivi di fattibilità (pilot) e di efficacia (studio completo)
4. La regola d'oro (una fase alla volta, con conferma esplicita)

Poi avvia la **Fase 1** (o la fase successiva a quella già completata).

---

## File generati dalla Skill

Crea tutti i file nella **cartella di lavoro corrente**. Se non è chiaro quale sia, chiedi all'utente di specificarla prima di procedere.

1. `protocollo_ricerca.md` — Il documento principale, aggiornato fase per fase. Struttura:
   ```
   # Protocollo di Ricerca — [Titolo Studio]
   <!-- Blocco STATO -->
   ## 1. Introduzione e Motivazione
   ## 2. Framework Teorico
   ## 3. Domande di Ricerca e Ipotesi
   ## 4. Partecipanti e Campione
   ## 5. Research Design
   ## 6. Variabili (IV, DV, Covariate)
   ## 7. Power Analysis
   ## 8. Procedura e Intervento
   ## 9. Piano di Analisi
   ## 10. Considerazioni Etiche
   ## 11. Riferimenti
   ```
2. `strumenti_valutazione.md` — Test, questionari validati e tracce per le interviste.
3. `timeline_pilota.md` — Pianificazione settimanale (Gantt) delle attività sul campo.
4. `preprint_bozza.md` — Bozza del paper scientifico in formato IMRAD, generata nella Fase 6.

### Blocco STATO (ottimizzazione contesto)

All'inizio di ogni sessione e dopo ogni fase completata, mantieni aggiornato il **Blocco STATO** nelle prime righe di `protocollo_ricerca.md`:

```
<!-- STATO
Fase corrente: [N]
Contesto: [secondaria/università/altro]
Framework: [es. SRL/Zimmerman]
Design: [es. Explanatory Sequential, quasi-sperimentale]
N previsto: [es. 40, 2 classi]
PRISMA: [nome file o "nessuno"]
RAG: [sì/no — indica se esiste rag_db/ nella cartella di lavoro]
Dati raccolti: [sì/no]
Ultima modifica: [data]
-->
```

**Alla ripresa di sessione:** leggi solo il Blocco STATO (non l'intero file) per ripristinare il contesto in pochi token. Leggi le sezioni specifiche del file solo quando la fase corrispondente è in esecuzione.

---

## Workflow Interattivo

### FASE 1: Framework Iniziale e Ipotesi

Poni le domande **una alla volta in modo conversazionale**: aspetta la risposta dell'utente prima di passare alla successiva. Non elencare tutte e 4 insieme.

1. Qual è l'**Obiettivo Principale** del pilota? Distingui: obiettivi di *fattibilità* (es. "verificare che il chatbot sia usabile da studenti liceali") da obiettivi di *efficacia* (es. "migliorare il punteggio MSLQ").
2. Qual è il **Framework Teorico** di riferimento? (es. Self-Regulated Learning di Zimmerman, Self-Determination Theory, UTAUT/TAM per l'adozione tecnologica). Il framework guida la scelta degli strumenti e la formulazione delle ipotesi.
3. Quali sono le **Domande di Ricerca (RQ)** e le **Ipotesi (H1, H0)**?
   Se l'utente non sa come formularle, proponi questo template e adattalo insieme:
   ```
   RQ1: [Variabile dipendente] degli studenti che usano [intervento] differisce
        significativamente da quella del gruppo di controllo dopo [N] settimane?
   H1:  Il gruppo sperimentale mostrerà [outcome] significativamente maggiore
        rispetto al gruppo di controllo (d ≥ [valore da PRISMA o 0.5]).
   H0:  Non vi è differenza significativa tra i gruppi (d ≈ 0).
   ```
   Se è disponibile un report PRISMA, usa l'effect size medio come benchmark per d in H1.
4. Qual è la **Popolazione e il Campione** previsto? (es. 2 classi di liceo, N=40)

**Se l'utente ha una revisione PRISMA disponibile**, estrai da essa e inserisci nel protocollo:
- Il **gap identificato** → diventa la motivazione del pilot (sezione Introduzione)
- Il **framework teorico emergente** dalla letteratura → integra o conferma la risposta al punto 2
- Le **RQ non ancora indagate** nella letteratura → affina le ipotesi del punto 3
- Le **caratteristiche dei campioni** degli studi inclusi → orienta la scelta del campione al punto 4

**Azione:** Leggi `protocollo_ricerca.md` se già esiste, poi aggiorna o crea le sezioni: Introduzione, Framework Teorico, Obiettivi, Ipotesi, Partecipanti. Se disponibile, aggiungi "Giustificazione dallo studio bibliografico" con i risultati PRISMA. Aggiorna il **Blocco STATO** con `Fase corrente: 1` e i campi Framework e N previsto. Chiedi conferma esplicita prima di procedere.

---

### FASE 2: Design della Ricerca (Mixed-Methods)

**2a. Design Quantitativo**
Suggerisci il design più adatto:
- *Quasi-sperimentale Pre-test/Post-test con Gruppo di Controllo* (se hai 2+ classi)
- *Within-subjects* (se hai una sola classe, con crossover o misure ripetute)

**Avvisi metodologici:**
- *Non-equivalenza dei gruppi:* In un quasi-esperimento i gruppi non sono assegnati casualmente. Verifica l'equivalenza baseline (t-test o ANCOVA sul pre-test) e riporta le covariate rilevanti.
- *Testing effect:* Il pre-test può sensibilizzare gli studenti e gonfiare il post-test. Valuta se usare un design Solomon a 4 gruppi se la contaminazione è probabile.
- *Attrition differenziale:* Il dropout non casuale tra i gruppi invalida i confronti. Pianifica come gestirlo (intento-a-trattare vs. per-protocol analysis) e registra i motivi di abbandono.

**2b. Design Mixed-Methods — scegli il tipo**
Non tutti i design MM sono equivalenti. Scegli in base alle tue domande di ricerca:

| Design | Logica | Quando usarlo |
|---|---|---|
| *Convergent Parallel* | Quant e qual raccolti in parallelo, integrati alla fine | Quando vuoi confrontare/triangolare le due fonti |
| *Explanatory Sequential* | Prima quant, poi qual per spiegare risultati inattesi | Quando vuoi capire *perché* i numeri dicono quello che dicono |
| *Exploratory Sequential* | Prima qual, poi quant per generalizzare | Quando il fenomeno è poco noto e vuoi costruire strumenti |

Per pilot su AI in classe, il design più comune è **Explanatory Sequential**.

**2c. Variabili**
- Variabile Indipendente: l'intervento Ed-Tech (es. uso del chatbot RAG)
- Variabili Dipendenti: gli outcome misurabili (es. punteggio MSLQ, voti)
- Covariate: sesso, background tecnologico, conoscenze pregresse

**2d. Power Analysis**
Per studi pilota, la power analysis serve principalmente a **stimare l'effect size** per lo studio completo, non a garantire potenza sufficiente nel pilot stesso:
- Riferimento orientativo pilota: N ≥ 30 per gruppo è una soglia di massima. Se il campione disponibile è inferiore (es. una sola classe, N=20), il pilot rimane valido ai fini della fattibilità — dichiara esplicitamente che la potenza statistica è insufficiente per conclusioni sull'efficacia e che il risultato principale è la stima dell'effect size per il dimensionamento futuro.
- Riporta l'effect size ottenuto nel pilot come input per il dimensionamento futuro.

**Se è disponibile una revisione PRISMA**, usa gli effect size degli studi inclusi come stima a priori più informata (es. d medio ponderato dalla meta-analisi) al posto del valore convenzionale d = 0.5. Questo rende la power analysis molto più solida e giustificabile ai reviewer.

**Passi operativi G*Power** (per stimare N nello studio completo):
1. Apri G*Power → `F tests` → `ANOVA: Fixed effects, main effects and interactions` (o `t-tests → Means: Two independent groups` per confronti semplici)
2. Inserisci: Effect size d (es. 0.5 da PRISMA), α = .05, Power = .80, N groups = 2
3. Clicca `Calculate` → G*Power restituisce N per gruppo
4. Riporta nel protocollo: *"Per rilevare d = [X] con α = .05 e potenza = .80, lo studio completo richiede N = [Y] per gruppo (G*Power 3.1)."*
5. Confronta con il N del pilot: se il pilot ha meno del 50% del N richiesto, enfatizza che i risultati sono preliminari.

Chiedi all'utente se ha già un N previsto e valuta insieme se è sufficiente agli obiettivi.

**Azione:** Leggi `protocollo_ricerca.md`, poi aggiorna la sezione Research Design e Variabili mantenendo tutto il contenuto precedente. Aggiorna il **Blocco STATO** con `Fase corrente: 2` e il campo Design. Chiedi conferma.

---

### FASE 3: Strumenti e Misure

**3a. Misure Quantitative — Questionari validati**

| Costrutto | Strumento | Note |
|---|---|---|
| Self-Regulated Learning | MSLQ (Pintrich et al., 1991) | 81 item, 15 sottoscale; verifica validità sottoscale in italiano |
| Accettazione tecnologia | TAM (Davis, 1989) | 12 item, PU + PEU |
| Carico cognitivo | NASA-TLX (Hart & Staveland, 1988) | 6 dimensioni |
| Engagement | UWES-S (Schaufeli et al., 2002) | versione studenti |
| Atteggiamento verso l'AI | GAAIS (Schepman & Rodway, 2020) | scala generale fiducia/atteggiamento AI |
| Qualità interazione AI | AIQUE (Laupichler et al., 2023) | specifica per contesti educativi con AI — **REGOLA:** prima di usare qualsiasi strumento, verifica item, sottoscale e disponibilità versione italiana dalla fonte primaria. Non affidarsi mai alla memoria del modello per i dettagli psicometrici degli strumenti. |

Per ogni strumento scelto, ricorda di:
- Verificare l'**affidabilità** (α di Cronbach ≥ .70 atteso) sui tuoi dati
- Verificare la **validità di costrutto** (validità convergente e discriminante), non solo l'affidabilità
- Preferire versioni tradotte e validate in italiano quando disponibili

**Se è disponibile una revisione PRISMA**, controlla quali strumenti sono stati più usati negli studi inclusi: la convergenza su uno strumento in più studi è evidenza di fatto della sua adozione nel campo e facilita il confronto dei risultati con la letteratura esistente. Segnalalo all'utente come criterio aggiuntivo di scelta.

**3b. Misure Qualitative**
Stendi 4-5 domande aperte per interviste o focus group. Esempi:
- "Descrivi come hai usato l'AI nelle ultime settimane di studio."
- "Qual è stata la sfida maggiore nell'usare il chatbot per studiare?"
- "In che modo ti ha aiutato (o ostacolato) nel pianificare il tuo studio?"

Se il coding è svolto da più ricercatori, prevedi una procedura di **inter-rater agreement** (Cohen's κ ≥ .70).

**3c. Learning Analytics (Opzionale)**
Definisci *quali* dati di sistema raccogliere (non come estrarli tecnicamente). Esempi concreti:
- Numero di prompt inviati per sessione
- Durata media delle sessioni
- Frequenza di accesso (giorni attivi/settimana)
- Tipologia delle richieste (classificazione manuale o automatica a posteriori)

**Azione:** Crea `strumenti_valutazione.md` con questa struttura per ogni strumento scelto. Aggiorna il **Blocco STATO** con `Fase corrente: 3`.

```markdown
# Strumenti di Valutazione — [Titolo Studio]

## Strumenti Quantitativi

### [Nome strumento] — [Costrutto misurato]
**Riferimento:** [Autore, Anno]
**N item / sottoscale:** [es. 81 item, 15 sottoscale]
**Tempo somministrazione:** [es. 15-20 min]
**Scala risposta:** [es. Likert 1-7]
**Scoring:** [es. media per sottoscala; punteggi alti = maggiore SRL]
**Versione italiana:** [disponibile / da verificare / non disponibile]
**Affidabilità attesa:** α di Cronbach ≥ .70 — verifica sui tuoi dati
**Note:** [es. adattamenti per minori, eventuali item eliminati]

---

## Traccia Interviste / Focus Group

**Domande principali:**
1. [Domanda aperta 1]
2. [Domanda aperta 2]
...

**Probe suggeriti:** [es. "Puoi farmi un esempio?", "Come ti sei sentito in quel momento?"]
**Durata prevista:** [es. 20-30 min per intervista]
**Metodo registrazione:** [audio con consenso / note scritte]

---

## Learning Analytics (se applicabile)

| Dato raccolto | Fonte (sistema) | Frequenza | Note privacy |
|---|---|---|---|
| [es. N prompt/sessione] | [log chatbot] | [per sessione] | [anonimizzato] |
```

Chiedi conferma.

---

### FASE 4: Procedura e Intervento Pedagogico

Definisci cosa succede concretamente in classe:
1. Qual è il ruolo del docente durante l'intervento?
2. Quanto dura il pilota? Adatta al **calendario scolastico italiano**: evita periodi di scrutinio (febbraio, giugno), giornate di orientamento, o settimane precedenti agli esami. Un pilota realistico in una scuola secondaria italiana è tipicamente 3-5 settimane effettive, non 4 settimane continuative.
3. Cosa fa il **gruppo di controllo** mentre lo sperimentale usa la tecnologia? (Cruciale per la validità interna — se privare il gruppo di controllo è eticamente problematico, suggerisci un **wait-list design**: il gruppo di controllo riceve lo stesso intervento in un secondo momento, dopo la fine del pilot; tutti i partecipanti accedono alla tecnologia, ma in momenti diversi. Elimina il problema etico e consente un confronto pre/post all'interno del gruppo di controllo quando riceve l'intervento.)
4. **Fidelity check:** come si verifica che l'intervento sia somministrato come previsto? (es. log di accesso, checklist docente, osservazione in classe)
5. **Vincoli burocratici italiani:** ricorda all'utente di ottenere: autorizzazione del Dirigente Scolastico, consenso informato dei genitori (GDPR minori, D.Lgs. 196/2003 + Reg. EU 679/2016), eventuale notifica al DPO dell'istituto se si raccolgono dati personali digitali.

   > **Azione aggiuntiva:** chiedi: *"Vuoi che generi un modulo di consenso informato per i genitori, conforme al GDPR?"* Se sì, genera un documento con: intestazione istituto, descrizione dello studio in linguaggio non tecnico, dati raccolti e finalità, soggetto titolare del trattamento, diritti dell'interessato (art. 15-22 GDPR), firma genitore + data, firma ricercatore. Avvisa che il testo va verificato dal DPO o dal legale dell'istituto prima dell'uso.

**Azione:** Crea `timeline_pilota.md` con cronoprogramma:
- Settimana 1: Pre-test e Onboarding
- Settimane 2-3: Intervento (con fidelity check a metà percorso)
- Settimana 4: Post-test, Interviste/Focus Group

Aggiorna la procedura in `protocollo_ricerca.md`. Aggiorna il **Blocco STATO** con `Fase corrente: 4`. Chiedi conferma.

---

### FASE 5: Piano di Analisi Dati, Integrazione e Etica

**5a. Analisi Quantitativa**
- ANCOVA (controllando pre-test e covariate) per il confronto tra gruppi
- t-test appaiati per confronti within-subjects
- Regressione multipla per esplorare predittori
- Riporta sempre la **dimensione dell'effetto** (Cohen's d o η²) e gli **intervalli di confidenza** al 95%
- **Missing data:** specifica la strategia (listwise deletion solo se MCAR verificato; altrimenti multiple imputation o FIML)
- Verifica le assunzioni dell'ANCOVA: normalità dei residui, omoschedasticità, omogeneità dei pendii di regressione

**5b. Analisi Qualitativa — Thematic Analysis (Braun & Clarke, 2006)**

Segui i 6 step nell'ordine. Non saltarne nessuno — ogni step è prerequisito del successivo:

1. **Familiarizzazione** — Trascrivi le interviste (verbatim). Leggi tutto il corpus più volte, prendi note iniziali su idee ricorrenti. Non ancora coding.
2. **Coding** — Etichetta sistematicamente ogni estratto rilevante con un codice descrittivo breve (es. *"frustrazione interfaccia"*, *"autonomia percepita"*). Usa un software (NVivo, Atlas.ti, o semplicemente un foglio Excel con colonne testo/codice/partecipante).
3. **Generazione temi** — Raggruppa i codici in temi potenziali più ampi. Un tema cattura qualcosa di significativo rispetto alla RQ, non è solo un argomento ricorrente.
4. **Revisione temi** — Verifica che ogni tema sia internamente coerente e distinto dagli altri. Rileggi tutti gli estratti sotto ogni tema: se non si adattano, ricodifica o ridefinisci il tema.
5. **Definizione e denominazione** — Scrivi una definizione chiara per ogni tema finale. Il nome deve catturare l'essenza, non essere un'etichetta generica (es. *"Dipendenza strumentale vs. autonomia riflessiva"* invece di *"Uso AI"*).
6. **Scrittura** — Costruisci la narrativa per ogni tema con citazioni esemplificative (non più di 2-3 per tema nel paper). La citazione deve *illustrare*, non *sostituire* l'analisi.

**Inter-rater agreement:** se disponibile un secondo codificatore, calcola Cohen's κ dopo lo step 2. Se κ < .70, discuti le discordanze, ricodifica, ricalcola. Riporta κ finale nel paper.

**5c. Integrazione Mixed-Methods (Triangolazione)**
Definisci esplicitamente il punto di convergenza dei dati:
- In quale fase si confrontano risultati quantitativi e qualitativi?
- Come si gestiscono le *divergenze*? (es. il post-test migliora ma le interviste riportano frustrazione)

Usa un **joint display** per presentare l'integrazione nel paper. Struttura standard:

```
| Tema qualitativo         | Dati quantitativi correlati    | Interpretazione integrata        |
|--------------------------|-------------------------------|----------------------------------|
| Autonomia vs. dipendenza | MSLQ autoregolazione: +0.4 SD | Gli studenti dichiarano autonomia |
|                          | (t(38)=2.1, p=.04, d=0.67)    | ma i dati mostrano uso passivo   |
| Frustrazione interfaccia | TAM PEU: M=3.2 (basso)        | Conferma: usabilità è la barriera|
|                          | dropout settimana 2: 3 su 20  | principale all'adozione          |
```

**Divergenze:** se i dati quant e qual contraddicono, non nasconderlo — è un risultato prezioso. Riporta la divergenza e offri ipotesi interpretative (es. *"Il miglioramento MSLQ potrebbe riflettere desiderabilità sociale piuttosto che cambiamento reale, come suggerito dalle interviste"*).

**5d. Pre-registrazione**
Suggerisci all'utente di pre-registrare lo studio su **OSF** (osf.io) prima della raccolta dati. Vantaggi: aumenta la credibilità, distingue analisi confermative da esplorative, sempre più richiesta dai reviewer di *Computers & Education*, *BJET*, *IJAIED*.

**Guida operativa OSF:** accedi a osf.io → "Registrations" → "New Registration" → scegli il template "Pre-Registration" o "OSF Pre-registration". Campi minimi da compilare prima dell'avvio della raccolta dati:
- **Titolo e autori** dello studio
- **Ipotesi** (H1, H0 per ogni RQ — copia dal Protocollo)
- **Design** (quasi-sperimentale, N previsto, criteri di inclusione/esclusione partecipanti)
- **Variabili** (IV, DV, covariate — dal Protocollo)
- **Piano di analisi** (ANCOVA, t-test appaiati, soglia α — dal Protocollo)
- **Missing data strategy** (listwise deletion / multiple imputation)

Una volta registrato, il sistema genera un link permanente e con timestamp — includi questo link nella sezione Metodi del preprint. Le analisi esplorative aggiunte dopo la raccolta dei dati vanno dichiarate come tali ("exploratory analysis, not pre-registered").

**5e. Considerazioni Etiche**
Inserisci nel protocollo:
- **Consenso Informato** (dai genitori se i partecipanti sono minorenni)
- Approvazione formale dell'istituto scolastico
- Conformità al **GDPR**: anonimizzazione dei dati, finalità limitata, conservazione temporanea definita
- Se il gruppo di controllo non riceve l'intervento: valuta misure compensative post-studio

**Azione:** Completa `protocollo_ricerca.md`. Aggiorna il **Blocco STATO** con `Fase corrente: 5` e `Dati raccolti: no` (o `sì` se lo studio è già stato condotto). Presenta il riepilogo finale delle 5 sezioni compilate. Chiedi conferma, poi procedi alla **Fase 6**.

---

### FASE 6: Produzione del Preprint Scientifico

**Recap di coerenza (obbligatorio prima di scrivere)**
Leggi tutti e tre i file prodotti (`protocollo_ricerca.md`, `strumenti_valutazione.md`, `timeline_pilota.md`) e verifica:
- Il framework teorico della Fase 1 è coerente con gli strumenti scelti in Fase 3?
- Le RQ della Fase 1 sono tutte coperte dal piano di analisi della Fase 5?
- La procedura della Fase 4 è compatibile con la timeline prodotta?
Se trovi incoerenze, segnalale all'utente prima di procedere.

**Decisioni obbligatorie prima di scrivere**

Poni le seguenti domande in sequenza e attendi risposta prima di procedere:

1. *"Il preprint sarà in italiano o in inglese?"*
   - Italiano → adatta tutte le sezioni
   - Inglese → scrivi tutte le sezioni in inglese con titoli IMRAD standard

2. *"Che tipo di documento vuoi produrre: Protocol Paper (prima della raccolta dati), Results Paper (dopo), o Registered Report?"*

Dopo le risposte, dichiara esplicitamente: *"Produco un [tipo] in [lingua]. Inizio la stesura di `preprint_bozza.md`."* Non iniziare a scrivere prima di questa dichiarazione.

| Tipo | Quando | File struttura da leggere |
|---|---|---|
| **Protocol paper** | Prima della raccolta dati | `imrad-protocol-paper.md` |
| **Results paper** | Dopo la raccolta dati | `imrad-results-paper.md` |
| **Registered Report** | Prima dei dati, su invito rivista | `imrad-protocol-paper.md` (con nota pre-accettazione) |

**6a/6b. Strutture IMRAD**

Usa il tool **Read** sul file corrispondente al tipo scelto e usa quella struttura per generare `preprint_bozza.md`:
- Protocol paper → Read `~/.claude/skills/edtech-pilot-design/imrad-protocol-paper.md`
- Results paper → Read `~/.claude/skills/edtech-pilot-design/imrad-results-paper.md`

> **Fallback se i file non esistono:** usa direttamente la struttura qui sotto.
>
> **Protocol paper (fallback inline):** Abstract strutturato → 1. Introduction (gap + PRISMA + RQ) → 2. Methods (2.1 Design, 2.2 Participants, 2.3 Instruments, 2.4 Procedure, 2.5 Analysis Plan, 2.6 Ethics) → 3. Expected Outcomes → 4. Limitations → 5. References (APA 7).
>
> **Results paper (fallback inline):** stessa struttura del Protocol Paper con la sezione 3 sostituita da: 3.1 Quantitative Results (M, SD, ANCOVA, effect size + IC 95%), 3.2 Qualitative Results (temi da Thematic Analysis + inter-rater κ), 3.3 MM Integration (joint display) → 4. Discussion → 5. Conclusions.

Per studi pilota il tipo più comune è il Protocol Paper.

**Se il RAG è disponibile** (Blocco STATO `RAG: sì`): per ogni sezione del paper che cita letteratura, esegui una query mirata prima di scrivere: `py hybrid_rag.py query "<costrutto o topic sezione>" --n 3`. Cita solo paper recuperati dalla query — mai dalla memoria del modello (stesso guardrail di prisma-review).

---

**6c. Dove caricare il preprint**

| Server | Disciplina | Note |
|---|---|---|
| **EdArXiv** (edarxiv.org) | Educazione | Specifico per ricerca educativa |
| **PsyArXiv** (psyarxiv.com) | Psicologia/SRL | Ottimo per studi su apprendimento |
| **OSF Preprints** (osf.io) | Tutti | Integrato con pre-registrazione |
| **SSRN** (ssrn.com) | Scienze sociali | Ampia visibilità, accesso rapido |

Consiglia di caricare su **OSF** se lo studio è pre-registrato lì (coerenza); su **EdArXiv** per massima visibilità nel campo educativo.

**6d. Riviste target per la submission finale**

Chiedi all'utente se intende sottomettere a una rivista e guidalo nella scelta:

| Rivista | IF approx. | Tipo studio privilegiato | Note |
|---|---|---|---|
| *Computers & Education* | ~12 | Quasi-sperimentali, RCT, review | Top venue; richiede contributo teorico forte |
| *British Journal of Educational Technology (BJET)* | ~7 | Mixed-methods, design-based | Aperto a pilot ben motivati |
| *International Journal of AI in Education (IJAIED)* | ~5 | AI/ITS/chatbot in contesti educativi | Ottimo per studi su AI in classe |
| *Computers in Human Behavior* | ~10 | HCI, usabilità, adozione tecnologia | Ideale se il focus è TAM/UTAUT |
| *Education and Information Technologies* | ~5 | Ed-Tech applicata | Accetta pilot; peer review veloce |
| *Journal of Computer Assisted Learning* | ~5 | Learning design, interazione | Forte per approcci mixed-methods |

> **Nota:** gli IF sono indicativi (2023-24). Verifica il sito della rivista per le istruzioni agli autori (word count, APA/AMA, open access policy) prima di sottomettere.

---

**6d. Checklist di qualità prima della pubblicazione**
- [ ] Titolo include: design, popolazione, intervento, outcome
- [ ] Abstract strutturato con tutte le sezioni
- [ ] Framework teorico citato con riferimenti primari
- [ ] Strumenti citati con riferimento originale (non solo nome)
- [ ] Power analysis riportata con parametri espliciti
- [ ] Piano di analisi pre-specificato (no HARKing)
- [ ] Etica e GDPR dichiarati
- [ ] Riferimento alla pre-registrazione OSF (se effettuata)
- [ ] Revisione ortografica e stilistica finale

---

**Azione:** Genera `preprint_bozza.md` compilando le sezioni dai file prodotti nelle fasi precedenti. Al termine, chiedi se l'utente vuole esportare il preprint in formato Word.
- Se sì → invoca la skill **`pandoc-export`** tramite il tool `Skill` di Claude Code, passando `preprint_bozza.md`. Se la skill non è disponibile o fallisce, avvisa: *"La skill `pandoc-export` non è accessibile. Puoi convertire manualmente il file con: `pandoc preprint_bozza.md -o preprint_bozza.docx`"*
- Se l'utente vuole esportare anche il protocollo → invoca `pandoc-export` su `protocollo_ricerca.md` (o suggerisci il comando manuale).

---

## Errori Comuni

| Errore | Correzione |
|---|---|
| Trattare il pilot come studio definitivo sull'efficacia | Il pilot serve a testare la fattibilità; l'efficacia va confermata nello studio completo |
| Non specificare il framework teorico | Senza teoria, la scelta degli strumenti è arbitraria e le ipotesi sono deboli |
| Usare "mixed-methods" senza specificare il design | Scegli tra Convergent, Explanatory Sequential o Exploratory Sequential |
| Ignorare il testing effect | Valuta il design Solomon se il pre-test può contaminare le risposte |
| Riportare solo p-value | Aggiungere sempre effect size e IC 95% |
| Non pianificare i missing data | Decidere la strategia prima della raccolta, non dopo |

---

## Best Practices per l'Assistente

**Comportamento generale**
- Sii un mentore metodologico, non un esecutore passivo.
- Non procedere alla fase successiva senza conferma esplicita dell'utente.
- Se l'utente propone un design non etico, suggerisci il wait-list design.
- Mantieni un tono accademico, chiaro e strutturato.

**Guardrail anti-allucinazione — OBBLIGATORI**
- **Non inventare mai citazioni bibliografiche.** Usa sempre `[CITARE: autore/anno da verificare]` come segnaposto. Anche se conosci un autore con alta confidenza, metti il segnaposto: è l'utente che verifica, non il modello.
- **Versioni italiane degli strumenti:** non affermare mai che esiste una versione italiana validata senza che l'utente abbia confermato di averla trovata. Di default: "verificare se disponibile versione italiana validata".
- **Effect size "tipici":** se l'utente non fornisce dati reali, usa d = 0.5 come valore convenzionale e dichiara esplicitamente che è una stima conservativa, non un dato empirico del dominio.

**Guardrail anti-bias — OBBLIGATORI**
- **Bias SRL/framework dominante:** prima di suggerire MSLQ, verifica che SRL sia effettivamente il framework teorico scelto in Fase 1. Se lo studio è centrato sull'adozione tecnologica, suggerisci TAM/UTAUT come framework primario. Non proporre MSLQ per default.
- **Bias ottimismo AI in educazione:** nella sezione Discussion o Expected Outcomes, bilancia sempre con almeno un riferimento a studi con risultati nulli o negativi sull'AI in educazione (es. effetti di novelty, dipendenza tecnologica, divario digitale).
- **Bias design anglosassone:** adatta sempre le raccomandazioni al contesto scolastico italiano (calendario MIUR, vincoli burocratici, GDPR minori). Non proporre design che presuppongono condizioni irrealistiche per una scuola secondaria italiana tipica.
