# Tasks

1. Remove any login/signup features you have as wallet integration itself acts as authentication already. If you wish to not remove it, please make sure you have a definite reason when asked in your presentation.

2. As specified in prefinals, your notes app should be able to simulate building, signing, and submitting txs to the chain when doing Create, Update, and Delete operations in your notes app.

3. This time, instead of sending blank txs, attach a metadata to your tx containing all the necessary details you think should be attached. Of course, it is expected that you attach your actual note content in the metadata. Example code for that in JavaScript below. PLEASE READ THE CODE COMMENTS FOR YOUR REFERENCE!!!

   ```javascript
   // THIS ASSUMES YOU ARE USING `BLAZE` AS YOUR TX-BUILDER
   // MAKE SURE TO `import { Core } from "@blaze-cardano/sdk"` AT THE TOP OF YOUR FILE

   export const sendTransaction = async (provider, walletApi, targetAddress, lovelaceAmount, noteContent, action) => {
     
     // INITIALIZE WALLET AND BLAZE PROVIDER TO INTERACT WITH THE BLOCKCHAIN
     const wallet = new WebWallet(walletApi)
     const blaze = await Blaze.from(provider, wallet)

     // START BUILDING THE TRANSACTION: DEFINE PAYMENTS FIRST
     let tx = blaze
       .newTransaction()
       .payLovelace(
         Core.Address.fromBech32(targetAddress),
         lovelaceAmount,
       )

     // --- METADATA CONSTRUCTION STARTS HERE ---

     // STEP 1: INITIALIZE THE TOP-LEVEL CONTAINER (STANDARD JAVASCRIPT MAP)
     // THIS MAP HOLDS ALL METADATA FOR THE TRANSACTION
     // KEY = BIGINT (LABEL), VALUE = METADATUM (DATA)
     const metadata = new Map();

     // CHOOSE A UNIQUE LABEL FOR YOUR APP TO IDENTIFY ITS DATA ON-CHAIN
     // USE A RANDOM LARGE NUMBER TO AVOID COLLISIONS WITH OTHER DAPPS
     // DO NOT USE RESERVED LABELS (E.G., 721 FOR NFTS, 674 FOR MESSAGES) NOT IN
     // https://raw.githubusercontent.com/cardano-foundation/CIPs/master/CIP-0010/registry.json
     const label = 42819n; // MUST BE A BIGINT (NOTE THE 'n' SUFFIX)

     // STEP 2: CREATE THE INNER DATA STRUCTURE (MetadatumMap)
     // THIS ACTS LIKE A JSON OBJECT TO STORE YOUR SPECIFIC FIELDS
     const metadatumMap = new Core.MetadatumMap();

     // STEP 3: INSERT KEY-VALUE PAIRS INTO THE INNER MAP
     // IMPORTANT: BOTH KEYS AND VALUES MUST BE CONVERTED TO 'METADATUM' TYPES
     
     // INSERT 'ACTION' (CREATE, UPDATE, DELETE)
     metadatumMap.insert(
       Core.Metadatum.newText("action"),
       Core.Metadatum.newText(action)
     );

     // INSERT 'NOTE' CONTENT
     // WE USE A HELPER FUNCTION 'formatContent' HERE BECAUSE CARDANO HAS A 
     // STRICT 64-BYTE LIMIT PER STRING. IF THE NOTE IS LONG, IT MUST BE CHUNKED.
     metadatumMap.insert(
       Core.Metadatum.newText("note"),
       formatContent(noteContent || "") // FUNCTION DEFINITION IS EXPLAINED AFTER THIS CODE BLOCK
     );

     // INSERT 'TIMESTAMP' FOR SORTING LATER
     metadatumMap.insert(
       Core.Metadatum.newText("created_at"),
       Core.Metadatum.newText(new Date().toISOString())
     );

     // YOU CAN ALSO INSERT 'note_id' TO YOUR METADATA FOR BETTER REFERENCE
     
     // STEP 4: WRAP THE INNER 'METADATUMMAP' INTO A GENERIC 'METADATUM' OBJECT
     const metadatum = Core.Metadatum.newMap(metadatumMap);

     // STEP 5: ASSIGN THE DATA TO YOUR SPECIFIC LABEL IN THE TOP-LEVEL MAP
     metadata.set(label, metadatum);

     // STEP 6: CONVERT THE JAVASCRIPT MAP TO THE FINAL 'METADATA' TYPE REQUIRED BY BLAZE
     const finalMetadata = new Core.Metadata(metadata);

     // STEP 7: ATTACH THE METADATA TO THE TRANSACTION
     tx.setMetadata(finalMetadata);

     // --- FINALIZATION ---

     // BUILD, SIGN, AND SUBMIT THE TRANSACTION
     const completedTx = await tx.complete()
     const signedTx = await blaze.signTransaction(completedTx)
     const txId = await blaze.provider.postTransactionToChain(signedTx)
     return txId
   }
   ```

4. Since Cardano limits per string in metadata to 64-bytes, you are REQUIRED to implement a "chunking" mechanism. You cannot simply attach a long string to the metadata, or the transaction will fail. You must use a helper function that detects if a string is too long and splits it into a list of smaller strings. Sample helper function used in the code block above for formatting the note content:

   ```javascript
   // HELPER FUNCTION: FORMAT CONTENT
   // PURPOSE: CARDANO METADATA STRINGS CANNOT EXCEED 64 BYTES.
   // THIS FUNCTION CHECKS THE LENGTH. IF IT IS SHORT, IT RETURNS A SIMPLE TEXT.
   // IF IT IS LONG, IT SPLITS THE TEXT INTO CHUNKS AND RETURNS A LIST.

   const formatContent = (content) => {
     // CASE 1: SHORT STRING (FITS IN ONE CHUNK)
     if (content.length <= 64) {
       return Core.Metadatum.newText(content);
     }

     // CASE 2: LONG STRING (NEEDS SPLITTING)
     // REGEX SPLITS THE STRING EVERY 64 CHARACTERS
     const chunks = content.match(/.{1,64}/g) || [];
     const list = new Core.MetadatumList();
     
     chunks.forEach(chunk => {
       list.add(Core.Metadatum.newText(chunk));
     });

     return Core.Metadatum.newList(list);
   };
   ```

   It will look like this after successfully submitting a transaction:

   ```json
   {
     "action": "demo",
     "note": [
       "Remove any login/signup features you have as wallet integration ",
       "itself acts as authentication already. If you wish to not remove",
       "it, please make sure you have a definite reason when asked in y",
       "our presentation.",
       "As specified in prefinals, your notes app should be able to simu",
       "late sending txs when doing Create, Update, and Delete.",
       "This time, instead of sending blank txs, attach a metadata to yo",
       "ur tx containing all the necessary details you think should be a",
       "ttached. Of course, it is expected that you attach your actual n",
       "ote content in the metadata. Example code for that in JavaScript",
       ":",
       ""
     ],
     "created_at": "2025-12-01T07:35:07.339Z"
   }
   ```

5. Use the sendTransaction() function defined above to send the transaction on-chain, while simultaneously storing your notes to your local database. WHY? 
   Blockchain transactions take approximately 20 seconds to confirm on Cardano. A standard user will not wait 20 seconds to see their note appear on the screen. THAT IS BAD UX DESIGN.
   You must display the note immediately upon clicking save. Querying a database is milliseconds; querying the blockchain history takes time. The database acts as a fast cache.
   In that case, just architect your database to include a Status column with an initial value of "Pending" so to signify that this note is yet to be confirmed. Display this status in your notes app UI also.
   SUGGESTED DATABASE COLUMNS: id, address, txhash, status, note_content (anything beyond this is up to you)

6. You should already have a Blockfrost PROJECT ID at this point. Read and refer to the blockfrost documentation for the available APIs you can use to communicate with the blockchain. Open the Blockfrost API Client to test out APIs.

7. IMPORTANT: Implement an Asynchronous Background Worker. To handle the state synchronization between your local database and the blockchain, you must implement a background process (a worker). This script should run continuously (e.g., every 20 seconds) to check the status of pending transactions. This is so that you can continuously check if your notes has already been published successfully to the chain and update your UI status. For you to implement this, follow this:
   - Query your local database for all notes with status = 'pending'.
   - For each local note, take its corresponding tx_hash and query the Blockfrost API.
   - For preview network, use the API_BASE_URL=https://cardano-preview.blockfrost.io/api/v0
   - You can use the endpoint path /txs/{hash} to see if you can query a txhash. 
   - If Blockfrost returns the transaction details (200 OK): It means the transaction is included in a block. Update your local database notes' status to 'confirmed'.
   - If Blockfrost returns "Not Found" (404): The transaction is not yet confirmed. Do nothing and check again in the next interval.