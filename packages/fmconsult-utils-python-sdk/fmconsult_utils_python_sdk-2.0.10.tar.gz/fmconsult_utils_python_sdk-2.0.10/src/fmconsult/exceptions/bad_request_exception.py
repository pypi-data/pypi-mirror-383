class BadRequestException(Exception):

    def __init__(self, 
                 message="he request is malformed or missing required parameters",
                 response_body=None,
                 request_details=None
    ):
        self.status = 'bad request'
        self.message = message
        self.status_code = 400
        self.response_body = response_body
        self.request_details = request_details
        super().__init__(self.message)