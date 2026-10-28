import { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  Pressable,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { router, useLocalSearchParams } from 'expo-router';

export default function OfferRideScreen() {
  const { userId } = useLocalSearchParams();

  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [departureDate, setDepartureDate] = useState('');
  const [departureTime, setDepartureTime] = useState('');
  const [availableSeats, setAvailableSeats] = useState('');

  const handleCreateJourney = async () => {
    if (
      !origin ||
      !destination ||
      !departureDate ||
      !departureTime ||
      !availableSeats
    ) {
      Alert.alert(
        'Missing information',
        'Please complete all fields.'
      );
      return;
    }

    try {
      const response = await fetch(
        'http://192.168.1.106:5001/api/journeys',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            driverId: Number(userId),
            origin,
            destination,
            departureDate,
            departureTime,
            availableSeats: Number(availableSeats),
          }),
        }
      );

      const data = await response.json();

      if (response.ok) {
        Alert.alert(
          'Success',
          'Journey created successfully!',
          [
            {
              text: 'OK',
              onPress: () => router.back(),
            },
          ]
        );
      } else {
        Alert.alert(
          'Unable to create journey',
          data.message
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
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <View style={styles.form}>
        <Text style={styles.title}>Offer a Ride</Text>

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
          placeholder="Time - e.g. 08:00"
          placeholderTextColor="#777777"
          value={departureTime}
          onChangeText={setDepartureTime}
        />

        <TextInput
          style={styles.input}
          placeholder="Available seats"
          placeholderTextColor="#777777"
          keyboardType="number-pad"
          value={availableSeats}
          onChangeText={setAvailableSeats}
        />

        <Pressable
          style={styles.button}
          onPress={handleCreateJourney}
        >
          <Text style={styles.buttonText}>
            Create Journey
          </Text>
        </Pressable>

        <Pressable onPress={() => router.back()}>
          <Text style={styles.backText}>Back</Text>
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
    justifyContent: 'center',
  },

  form: {
    padding: 24,
  },

  title: {
    fontSize: 32,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 30,
    color: '#111111',
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

  button: {
    backgroundColor: '#111111',
    padding: 16,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 10,
  },

  buttonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '600',
  },

  backText: {
    textAlign: 'center',
    marginTop: 20,
    fontSize: 16,
    color: '#111111',
  },
});