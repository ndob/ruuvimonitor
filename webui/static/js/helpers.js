// Helpers

function getLocalTimestampRaw(tsString) {
    try {
         // Offset in milliseconds.
        let localTimeOffset = (new Date()).getTimezoneOffset() * 60000;
        let localISOTime = (new Date(new Date(tsString + "Z") - localTimeOffset)).toISOString().slice(0, -1);
        return localISOTime;
    } catch (ex) {
        return tsString;
    }
}

function getLocalTimestamp(tsString) {
    try {
        return getLocalTimestampRaw(tsString).replace("T", " ").slice(0, -4);
    } catch (ex) {
        return tsString;
    }
}

function getLocalTimestampTimeOnly(tsString) {
    try {
        return getLocalTimestampRaw(tsString).split("T")[1].slice(0, -4);
    } catch (ex) {
        return tsString;
    }
}

function getLocalTimestampDateOnly(tsString) {
    try {
        return getLocalTimestampRaw(tsString).split("T")[0];
    } catch (ex) {
        return tsString;
    }
}
