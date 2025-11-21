import { Blaze, Blockfrost, Core, WebWallet } from '@blaze-cardano/sdk'
import { useState, useEffect } from 'react'

function App() {
  const [wallets, setWallets] = useState([])
  const [walletApi, setWalletApi] = useState(null)
  const [selectedWallet, setSelectedWallet] = useState('')
  const [walletAddress, setWalletAddress] = useState('')
  const [recipient, setRecipient] = useState('')
  const [amount, setAmount] = useState(0n)
  const [provider] = useState(() => new Blockfrost({
    network: 'cardano-preview',
    projectId: import.meta.env.VITE_BLOCKFROST_PROJECT_ID,
  }))

  useEffect(() => {
    if (window.cardano) {
      setWallets(Object.keys(window.cardano))
    }
  }, [])

  const handleWalletChange = async (event) => {
    const walletName = event.target.value
    setSelectedWallet(walletName)
  }

  const handleConnectWallet = async () => {
    console.log('Connecting to wallet:', selectedWallet)
    if (selectedWallet && window.cardano[selectedWallet]) {
      try {
        const api = await window.cardano[selectedWallet].enable()
        setWalletApi(api)
        console.log('Connected to wallet API:', api)

        const address = await api.getChangeAddress();
        console.log('Wallet address:', address)
        setWalletAddress(address)
      } catch (error) {
        console.error('Error connecting to wallet:', error)
      }
    }
  }

  const handleRecipientChange = (event) => {
    setRecipient(event.target.value)
  }

  const handleAmountChange = (event) => {
    setAmount(BigInt(event.target.value))
  }

  const handleSubmitTransaction = async () => {
    if (walletApi) {
      try {
        const wallet = new WebWallet(walletApi)
        const blaze = await Blaze.from(provider, wallet)
        console.log('Blaze instance created:', blaze)

        const bech32Address = Core.Address.fromBytes(Buffer.from(walletAddress, 'hex')).toBech32()
        console.log('Recipient address (bech32):', bech32Address)

        const tx = await blaze
          .newTransaction()
          .payLovelace(
            Core.Address.fromBech32(recipient),
            amount
          )
          .complete()

        console.log('Transaction built:', tx.toCbor())

        const signedTx = await blaze.signTransaction(tx)

        console.log('Transaction signed:', signedTx.toCbor())

        const txHash = await blaze.provider.postTransactionToChain(signedTx)
        
        console.log('Transaction submitted. Hash:', txHash)
      } catch (error) {
        console.error('Error submitting transaction:', error)
      }
    }
  }

  return (
    <div>
      <div>
        <select value={selectedWallet} onChange={handleWalletChange}>
          <option value="">Select Wallet</option>
          {wallets.length > 0 && wallets.map((wallet) => (
            <option key={wallet} value={wallet}>{wallet}</option>
          ))}
        </select>
      </div>
      {walletApi ? 
        (<div>Wallet Connected</div>) : 
        (<button onClick={handleConnectWallet}>Connect Wallet</button>)
      }

      <div>
        <p>Connected Wallet Address: {walletAddress}</p>

        <label>Recipient Address: </label>
        <input type="text" placeholder="Enter Recipient Address" value={recipient} onChange={handleRecipientChange} />
        <br />
        <label>Amount: </label>
        <input type="number" placeholder="Enter Amount" value={amount} onChange={handleAmountChange} />
        <br />
        <button onClick={handleSubmitTransaction}>Send ADA</button>
      </div>
    </div>
  )
}

export default App