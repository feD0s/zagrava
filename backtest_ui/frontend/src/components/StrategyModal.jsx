import React, { useEffect, useState } from "react";

const StrategyModal = ({ active, handleModal, id, setErrorMessage }) => {
    const [name, setName] = useState("");
    const [windowSize, setWindowSize] = useState("");
    const [buyStakeSize, setBuyStakeSize] = useState("");
    const [buyBp, setBuyBp] = useState("");
    const [buyCooldown, setBuyCooldown] = useState("");
    const [buyMaxContracts, setBuyMaxContracts] = useState("");
    const [sellStakeSize, setSellStakeSize] = useState("");
    const [sellBp, setSellBp] = useState("");
    const [sellCooldown, setSellCooldown] = useState("");
    const [sellMinContracts, setSellMinContracts] = useState("");

    useEffect(() => {
      const getStrategy = async () => {
        const requestOptions = {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        };
        const response = await fetch(`/api/strategy/${id}`, requestOptions);

        if (!response.ok) {
          setErrorMessage("Couldn't fetch strategy");
        } else {
          const data = await response.json();
          setName(data.name);
          setWindowSize(data.windowSize);
          setBuyStakeSize(data.buyStakeSize);
          setBuyBp(data.buyBp);
          setBuyCooldown(data.buyCooldown);
          setBuyMaxContracts(data.buyMaxContracts);
          setSellStakeSize(data.sellStakeSize);
          setSellBp(data.sellBp);
          setSellCooldown(data.sellCooldown);
          setSellMinContracts(data.sellMinContracts);
        }
      };

      if (id) {
        getStrategy();
      }
    }, [id]);
      

    const cleanformData = () => {
        setName("");
        setWindowSize("");
        setBuyStakeSize("");
        setBuyBp("");
        setBuyCooldown("");
        setBuyMaxContracts("");
        setSellStakeSize("");
        setSellBp("");
        setSellCooldown("");
        setSellMinContracts("");
    };
    const handleCreateStrategy = async (e) => {
        e.preventDefault();
        const requestOptions = {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
                name: name,
                windowSize: windowSize,
                buyStakeSize: buyStakeSize,
                buyBp: buyBp,
                buyCooldown: buyCooldown,
                buyMaxContracts: buyMaxContracts,
                sellStakeSize: sellStakeSize,
                sellBp: sellBp,
                sellCooldown: sellCooldown,
                sellMinContracts: sellMinContracts,
            }),
        };
        const response = await fetch("/api/strategy", requestOptions);
        if (!response.ok) {
            setErrorMessage("Strategy creation failed");
        } else {
            cleanformData();
            handleModal();
        }
    };

    return (
      <div className={`modal ${active && "is-active"}`}>
        <div className="modal-background" onClick={handleModal}></div>
        <div className="modal-card">
          <header className="modal-card-head has-background-primary-light">
            <h1 className="modal-card-title">
              "Create Strategy"
            </h1>
          </header>
          <section className="modal-card-body">
            <form>
              <div className="field">
                <label className="label">Name</label>
                <div className="control">
                  <input
                    type="text"
                    placeholder="Enter strategy name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="input"
                    required
                  />
                </div>
              </div>
              <div className="field">
                <label className="label">Window Size</label>
                <div className="control">
                  <input
                    type="number"
                    placeholder="Enter window size"
                    value={windowSize}
                    onChange={(e) => setWindowSize(e.target.value)}
                    className="input"
                    required
                  />
                </div>
              </div>
              <div className="field">
                <label className="label">Buy Stake Size</label>
                <div className="control">
                  <input
                    type="number"
                    placeholder="Enter buy stake size"
                    value={buyStakeSize}
                    onChange={(e) => setBuyStakeSize(e.target.value)}
                    className="input"
                    required
                  />
                </div>
              </div>
              <div className="field">
                <label className="label">Buy BP</label>
                <div className="control">
                  <input
                    type="number"
                    placeholder="Enter buy bp"
                    value={buyBp}
                    onChange={(e) => setBuyBp(e.target.value)}
                    className="input"
                    required
                  />
                </div>
              </div>
              <div className="field">
                <label className="label">Buy Cooldown</label>
                <div className="control">
                  <input
                    type="number"
                    placeholder="Enter buy cooldown"
                    value={buyCooldown}
                    onChange={(e) => setBuyCooldown(e.target.value)}
                    className="input"
                    required
                  />
                </div>
              </div>
              <div className="field">
                <label className="label">Buy Max Contracts</label>
                <div className="control">
                  <input
                    type="number"
                    placeholder="Enter buy max contracts"
                    value={buyMaxContracts}
                    onChange={(e) => setBuyMaxContracts(e.target.value)}
                    className="input"
                    required
                  />
                </div>
              </div>
              <div className="field">
                <label className="label">Sell Stake Size</label>
                <div className="control">
                  <input
                    type="number"
                    placeholder="Enter sell stake size"
                    value={sellStakeSize}
                    onChange={(e) => setSellStakeSize(e.target.value)}
                    className="input"
                    required
                  />
                </div>
              </div>
              <div className="field">
                <label className="label">Sell BP</label>
                <div className="control">
                  <input
                    type="number"
                    placeholder="Enter sell bp"
                    value={sellBp}
                    onChange={(e) => setSellBp(e.target.value)}
                    className="input"
                    required
                  />
                </div>
              </div>
              <div className="field">
                <label className="label">Sell Cooldown</label>
                <div className="control">
                  <input
                    type="number"
                    placeholder="Enter sell cooldown"
                    value={sellCooldown}
                    onChange={(e) => setSellCooldown(e.target.value)}
                    className="input"
                    required
                  />
                </div>
              </div>
              <div className="field">
                <label className="label">Sell Min Contracts</label>
                <div className="control">
                  <input
                    type="number"
                    placeholder="Enter sell min contracts"
                    value={sellMinContracts}
                    onChange={(e) => setSellMinContracts(e.target.value)}
                    className="input"
                    required
                  />
                </div>
              </div>
            </form>
          </section>
            <footer className="modal-card-foot has-background-primary-light">
                <button className="button is-primary" onClick={handleCreateStrategy}>
                  Create
                </button>
                <button className="button" onClick={handleModal}>
                  Cancel
                </button>
            </footer>
        </div>
      </div>
    );
};

export default StrategyModal;