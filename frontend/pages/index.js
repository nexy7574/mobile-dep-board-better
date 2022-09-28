import Head from 'next/head'
import Image from 'next/image'
import { Component } from 'react'
import styles from '../styles/Home.module.css'
import loading from "../public/loader.gif";
import Link from 'next/link';


class Main extends Component {
  constructor(props) {
    super(props)
    this.state = {
      stop_id: null,
      timetable: {},
      last_refresh: null,
      loading: false,
      postcode: null,
      stops: null
    }
    this.handleForm.bind(this);
    this.handleNearbyStopsForm.bind(this);
    this.getNearestStops.bind(this);
  }

  componentDidMount() {
    this.setState({last_refresh: new Date()})
  }

  handleForm(event) {
    event.preventDefault();
    const _this = this;
    event.target.children[1].disabled = true;
    event.target.children[1].className = styles.lds_dual_ring;
    let _f = fetch("/api/stop?stop_id=" + event.target.stop_id.value);
    this.setState({loading: true});
    _f.then(
      (response) => {
        if(response.status === 404) {
          alert("Stop not found or no upcoming departures.");
          _this.setState({loading: false});
          event.target.children[1].disabled = false;
          event.target.children[1].className = null;
          return
        }
        else if (!response.ok) {
          alert("There was an issue loading the timetable. Please try again later.");
          _this.setState({loading: false});
          event.target.children[1].disabled = false;
          event.target.children[1].className = null;
          return
        }
        response.json().then(
          (data) => {
            event.target.children[1].disabled = false;
            event.target.children[1].className = null;
            _this.setState(
              {
                stop_id: event.target.stop_id.value,
                timetable: data,
                last_refresh: new Date(),
                loading: false
              }
            )
          }
        )
      }
    )
    f.catch(
      () => {
        alert("There was an issue loading the timetable. Please try again later.");
          _this.setState({loading: false});
          event.target.children[1].disabled = false;
          event.target.children[1].className = null;
      }
    )
  }

  async getNearestStops(update_state = false) {
    const options = {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0
    };

    let pos = await new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject, options);
    })
    const postcode_response = await fetch("//api.postcodes.io/postcodes?lon=" + pos.coords.longitude + "&lat=" + pos.coords.latitude);
    const postcode_data = await postcode_response.json();
    const postcode_result = postcode_data.result[0].postcode;
    const nearby_stops_response = await fetch("/api/nearby?postcode=" + postcode_result);
    const nearby_stops_data = await nearby_stops_response.json();
    if(update_state===true) {
      this.setState({postode: postcode_result, stops: nearby_stops_data});
    }
    return nearby_stops_data;
  }

  table() {
    if(!this.state.timetable) {
      return null;
    }
    return (
      <table className={styles.timetable}>
        <thead>
          <tr>
            <th>Bus No.</th>
            <th>Destination</th>
            <th>Stand</th>
            <th>ETA</th>
          </tr>
        </thead>
        <tbody>
        {
          Object.keys(this.state.timetable).map(
            // (bus) => <tr><td>this.state.timetable[bus]</td></tr>
            (bus) => {
              if(bus==="url") {
                return;
              };
              return (
                <tr key={bus + Math.random()}>
                  <td>{bus}</td>
                  <td>{this.state.timetable[bus].destination}</td>
                  <td>{this.state.timetable[bus].stand}</td>
                  <td>{this.state.timetable[bus].time}</td>
                </tr>
              )
            }
          )
        }
        </tbody>
      </table>
    )
  }

  handleNearbyStopsForm(event) {
    event.preventDefault();
    const _this = this;
    event.target.children[1].disabled = true;
    event.target.children[1].textContent = "Loading..."
    this.setState({loading: true});
    let _f = this.getNearestStops();
    _f.then(
      (data) => {
        event.target.children[1].disabled = false;
        event.target.children[1].textContent = "Fetch"
        _this.setState(
          {
            nearby_stops: data,
            last_refresh: new Date(),
            loading: false
          }
        )
      }
    )
  }

  render() {
    let buttonContent = this.state.loading ? <Image alt={"Loading (this may take up to a minute)..."} src={loading} height={32} width={32}/> : <span>Submit</span>
    return (
      <div className={styles.container}>
        <Head>
          <title>WYDepartureTimeTable</title>
          <meta name="description" content="View bus departure timetables on a nicer website" />
          <link rel="icon" href="/favicon.ico" />
        </Head>
  
        <main className={styles.main}>
          <h1 className={styles.title}>
            WYDepartureTimeTable
          </h1>
  
          <p className={styles.description}>
            A better west yorkshire metro departure timetable viewer.
          </p>
  
          <div>
            <form onSubmit={(event) => this.handleForm(event)} style={{verticalAlign: "baseline", alignItems: "baseline"}}>
              <input id={"stop_id"} name={"stop_id"} type={"text"} placeholder={"Stop ID"} />
              <button type={"submit"}>{buttonContent}</button>
            </form>
          </div>

          <p>You have selected stop: {this.state.stop_id || "No stop yet."}</p>
          <p>This timetable was last refreshed: {this.state.last_refresh ? this.state.last_refresh.toLocaleString() : 'never'}</p>
          {this.table()}
          <br/>
          <a href={this.state.timetable.url || "#"} target="_blank">
            Sourced from: {this.state.timetable.url || ""}
          </a>
        </main>
      </div>
    )
  }
}


export default Main