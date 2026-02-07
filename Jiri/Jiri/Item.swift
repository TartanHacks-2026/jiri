//
//  Item.swift
//  Jiri
//
//  Created by Nihal Josyula on 2/7/26.
//

import Foundation
import SwiftData

@Model
final class Item {
    var timestamp: Date
    
    init(timestamp: Date) {
        self.timestamp = timestamp
    }
}
