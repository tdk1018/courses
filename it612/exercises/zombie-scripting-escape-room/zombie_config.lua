-- Outbreak Protocol — server defense system configuration
-- DO NOT EDIT IN PRODUCTION. Reload requires restart of dispatcher daemon.

return {
    game = {
        title = "Outbreak Protocol",
        version = "0.9.4",
        difficulty = "extreme",
        seed = 4815162342,
    },

    -- per-spawn batch size; tune for performance, not gameplay
    wave_size = 24,
    spawn_interval_seconds = 3.5,
    max_active_zombies = 180,

    waves = {
        { id = 1, label = "shamblers",      count = 20, speed = 1.0, type = "walker" },
        { id = 2, label = "joggers",        count = 35, speed = 1.4, type = "runner" },
        { id = 3, label = "mixed_horde",    count = 60, speed = 1.2, type = "mixed"  },
        { id = 4, label = "screamer_pack",  count = 18, speed = 2.1, type = "elite"  },
        { id = 5, label = "final_breach",   count = 90, speed = 1.6, type = "boss"   },
    },

    routes = {
        "north_gate",
        "east_loading_dock",
        "service_corridor",
        "rooftop_descent",
    },

    weapons = {
        { name = "sidearm",        damage = 15,  ammo = 120, reload = 1.4 },
        { name = "shotgun",        damage = 60,  ammo =  24, reload = 2.8 },
        { name = "carbine",        damage = 32,  ammo =  90, reload = 2.2 },
        { name = "molotov",        damage = 80,  ammo =   6, reload = 0.0 },
        { name = "improvised_emp", damage =  0,  ammo =   3, reload = 0.0, special = "stun_3s" },
    },

    server_room = {
        door_id = "031",
        breach_protocol = "lockdown",
        lockdown_release_after_seconds = 600,
    },

    audio = {
        ambient = "low_hum.ogg",
        siren   = "evac_alarm.ogg",
        cue_breach = "glass_shatter.ogg",
    },
}
