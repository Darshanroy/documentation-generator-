"Sample testing"

      // Send POST request to Flask backend
      fetch('/get_response', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      })
