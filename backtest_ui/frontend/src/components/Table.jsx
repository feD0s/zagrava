import React, { useContext, useEffect, useState } from "react";

import ErrorMessage from "./ErrorMessage";
import StrategyModal from "./StrategyModal";

const Table = () => {
  const [strategies, setStrategies] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [loaded, setLoaded] = useState(false);
  const [activeModal, setActiveModal] = useState(false);
  const [id, setId] = useState(null);

  const handleDelete = async (name) => {
    const requestOptions = {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
    };
    const response = await fetch(`/api/strategy/${name}`, requestOptions);
    if (!response.ok) {
      setErrorMessage("Strategy deletion failed");
    }

    getStrategies();
  };

  const getStrategies = async () => {
    const requestOptions = {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    };
      const response = await fetch("/api/strategy", requestOptions);
      if (!response.ok) {
        setErrorMessage("Couldn't fetch strategies");
      } else {
          const data = await response.json();
          setStrategies(data);
          setLoaded(true);
      }
  };
    
    useEffect(() => {
      getStrategies();
    }, []);

    const handleModal = () => {
      setActiveModal(!activeModal);
      getStrategies();
      setId(null);
    };

    return (
      <>
        <StrategyModal
          active={activeModal}
          handleModal={handleModal}
          id={id}
          setErrorMessage={setErrorMessage}
        />
        <button
          className="button is-fullwidth mb-5 is-primary"
          onClick={() => setActiveModal(true)}
        >
          Create Strategy
        </button>
          <ErrorMessage message={errorMessage} />
          {loaded && strategies ? (
            <table className="table is-fullwidth">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Window Size</th>
                  <th>Buy Stake Size</th>
                  <th>Buy BP</th>
                  <th>Buy Cooldown</th>
                  <th>Buy Max Contracts</th>
                  <th>Sell Stake Size</th>
                  <th>Sell BP</th>
                  <th>Sell Cooldown</th>
                  <th>Sell Min Contracts</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {strategies.map((strategy) => (
                  <tr key={strategy.id}>
                    <td>{strategy.name}</td>
                    <td>{strategy.windowSize}</td>
                    <td>{strategy.buyStakeSize}</td>
                    <td>{strategy.buyBp}</td>
                    <td>{strategy.buyCooldown}</td>
                    <td>{strategy.buyMaxContracts}</td>
                    <td>{strategy.sellStakeSize}</td>
                    <td>{strategy.sellBp}</td>
                    <td>{strategy.sellCooldown}</td>
                    <td>{strategy.sellMinContracts}</td>
                      <td>
                        <button className="button mr-2 is-info is-small is-light">
                          Update
                        </button>
                        <button
                          className="button mr-2 is-small is-danger is-light"
                          onClick={() => handleDelete(strategy.name)}
                        >
                          Delete
                        </button>
                      </td>    
                  </tr>
                ))}
              </tbody>    
            </table>
          ) : (
              <p>Loading</p>
          )}
      </>
    );

};

export default Table;