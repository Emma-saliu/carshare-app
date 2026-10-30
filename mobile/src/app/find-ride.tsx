import { useState } from 'react';


import {
  View,
  Text,
  TextInput,
  Pressable,
  StyleSheet,
  Alert,
  ScrollView,
} from 'react-native';

import { router } from 'expo-router';


type Journey = {
  id: number;
  driverId: number;

  origin: string;
  destination: string;

  departureDate: string;
  departureTime: string;

  availableSeats: number;

  matchScore: number;

  geographicalScore: number;

  timeScore: number;
  timeDifference: number;

  extraDistance: number;

  pickupDistance: number;
  dropoffDistance: number;
};


export default function FindRideScreen() {

  const [origin, setOrigin] =
    useState('');

  const [destination, setDestination] =
    useState('');

  const [departureDate, setDepartureDate] =
    useState('');

  const [preferredTime, setPreferredTime] =
    useState('');

  const [journeys, setJourneys] =
    useState<Journey[]>([]);


  const handleSearch = async () => {

    if (
      !origin ||
      !destination ||
      !departureDate ||
      !preferredTime
    ) {

      Alert.alert(
        'Missing information',
        'Please complete all fields.'
      );

      return;
    }


    try {

      const url =
        'http://192.168.1.106:5001/api/journeys'
        +
        `?origin=${encodeURIComponent(origin)}`
        +
        `&destination=${encodeURIComponent(destination)}`
        +
        `&date=${encodeURIComponent(departureDate)}`
        +
        `&time=${encodeURIComponent(preferredTime)}`;


      const response =
        await fetch(url);


      const data =
        await response.json();


      if (!response.ok) {

        Alert.alert(
          'Search failed',
          data.message ||
          'Unable to search journeys.'
        );

        return;
      }


      setJourneys(data);


      if (data.length === 0) {

        Alert.alert(
          'No journeys found',
          'No compatible journeys were found.'
        );
      }

    } catch (error) {

      console.log(error);

      Alert.alert(
        'Connection error',
        'Could not connect to the CarShare server.'
      );
    }
  };


  return (

    <ScrollView
      contentContainerStyle={
        styles.container
      }
    >

      <Text style={styles.title}>
        Find a Ride
      </Text>


      <TextInput
        style={styles.input}
        placeholder="From"
        placeholderTextColor="#777777"
        value={origin}
        onChangeText={setOrigin}
      />


      <TextInput
        style={styles.input}
        placeholder="To"
        placeholderTextColor="#777777"
        value={destination}
        onChangeText={setDestination}
      />


      <TextInput
        style={styles.input}
        placeholder="Date - e.g. 30/10/2026"
        placeholderTextColor="#777777"
        value={departureDate}
        onChangeText={setDepartureDate}
      />


      <TextInput
        style={styles.input}
        placeholder="Preferred time - e.g. 08:00"
        placeholderTextColor="#777777"
        value={preferredTime}
        onChangeText={setPreferredTime}
      />


      <Pressable
        style={styles.searchButton}
        onPress={handleSearch}
      >

        <Text
          style={
            styles.searchButtonText
          }
        >
          Search
        </Text>

      </Pressable>


      {journeys.map(
        (journey) => (

          <View
            key={journey.id}
            style={styles.card}
          >

            <Text
              style={styles.route}
            >
              {journey.origin}
              {' → '}
              {journey.destination}
            </Text>


            <Text
              style={styles.match}
            >
              {journey.matchScore}% Match
            </Text>


            <Text
              style={styles.details}
            >
              Date:{' '}
              {journey.departureDate}
            </Text>


            <Text
              style={styles.details}
            >
              Driver leaves:{' '}
              {journey.departureTime}
            </Text>


            <Text
              style={styles.details}
            >
              Seats available:{' '}
              {journey.availableSeats}
            </Text>


            <View
              style={styles.scoreSection}
            >

              <Text
                style={
                  styles.scoreTitle
                }
              >
                Match breakdown
              </Text>


              <Text
                style={styles.details}
              >
                Route score:{' '}
                {journey.geographicalScore}%
              </Text>


              <Text
                style={styles.details}
              >
                Time score:{' '}
                {journey.timeScore}%
              </Text>


              <Text
                style={styles.details}
              >
                Time difference:{' '}
                {journey.timeDifference}
                {' minutes'}
              </Text>


              <Text
                style={styles.details}
              >
                Pickup distance from route:{' '}
                {journey.pickupDistance}
                {' km'}
              </Text>


              <Text
                style={styles.details}
              >
                Drop-off distance from route:{' '}
                {journey.dropoffDistance}
                {' km'}
              </Text>


              <Text
                style={styles.details}
              >
                Estimated extra distance:{' '}
                {journey.extraDistance}
                {' km'}
              </Text>

            </View>

          </View>
        )
      )}


      <Pressable
        onPress={() =>
          router.back()
        }
      >

        <Text
          style={styles.backText}
        >
          Back
        </Text>

      </Pressable>

    </ScrollView>
  );
}


const styles =
  StyleSheet.create({

    container: {
      flexGrow: 1,
      backgroundColor: '#ffffff',
      padding: 24,
      paddingTop: 80,
    },


    title: {
      fontSize: 36,
      fontWeight: 'bold',
      color: '#111111',
      marginBottom: 30,
    },


    input: {
      borderWidth: 1,
      borderColor: '#cccccc',
      borderRadius: 10,
      padding: 15,
      fontSize: 16,
      marginBottom: 15,
      color: '#111111',
      backgroundColor: '#ffffff',
    },


    searchButton: {
      backgroundColor: '#111111',
      padding: 16,
      borderRadius: 10,
      alignItems: 'center',
      marginBottom: 30,
    },


    searchButtonText: {
      color: '#ffffff',
      fontSize: 18,
      fontWeight: '600',
    },


    card: {
      borderWidth: 1,
      borderColor: '#dddddd',
      borderRadius: 12,
      padding: 18,
      marginBottom: 18,
      backgroundColor: '#ffffff',
    },


    route: {
      fontSize: 20,
      fontWeight: 'bold',
      color: '#111111',
      marginBottom: 8,
    },


    match: {
      fontSize: 22,
      fontWeight: 'bold',
      color: '#111111',
      marginBottom: 15,
    },


    scoreSection: {
      marginTop: 15,
      paddingTop: 15,
      borderTopWidth: 1,
      borderTopColor: '#eeeeee',
    },


    scoreTitle: {
      fontSize: 16,
      fontWeight: 'bold',
      color: '#111111',
      marginBottom: 8,
    },


    details: {
      fontSize: 15,
      color: '#555555',
      marginBottom: 5,
    },


    backText: {
      textAlign: 'center',
      marginTop: 20,
      marginBottom: 40,
      fontSize: 16,
      color: '#111111',
    },

  });
