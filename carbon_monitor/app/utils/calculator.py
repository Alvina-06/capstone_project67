INDIA_EMISSION_FACTOR = 0.82

def calculate_energy(power_kw, time_seconds):
    energy_kwh = power_kw * (time_seconds / 3600)
    return round(energy_kwh, 4)

def calculate_carbon(energy_kwh):
    carbon_kg = energy_kwh * INDIA_EMISSION_FACTOR
    return round(carbon_kg, 4)

def energy_to_carbon_direct(power_kw, time_seconds):
    energy = calculate_energy(power_kw, time_seconds)
    carbon = calculate_carbon(energy)
    return {
        "energy_kwh": energy,
        "carbon_kg":  carbon
    }

if __name__ == "__main__":
    
    result = energy_to_carbon_direct(2.0, 3600)
    print(result)